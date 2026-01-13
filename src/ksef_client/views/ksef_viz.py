import os
import sys
import base64
import argparse
from lxml import etree
from io import BytesIO

# Import logic from internal modules
from ..utils import qr_codes_generator
from ..utils.ksefcert import Certificate
from ..utils.ksefconfig import Config

def detect_fa_version(root):
    """Detects the FA version from the XML root element."""
    namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    kod_elem = root.find('.//ns:Naglowek/ns:KodFormularza', namespace)
    if kod_elem is not None:
        wariant = root.find('.//ns:Naglowek/ns:WariantFormularza', namespace)
        if wariant is not None:
            return wariant.text
    return None

def get_qr_base64(xml_bytes, ksef_number=None, base_url="https://ksef-test.mf.gov.pl"):
    """Generates KSeF QR code and returns it as base64 string."""
    try:
        seller_nip, issue_date = qr_codes_generator.get_seller_nip_and_issue_date_from_invoice_xml_bytes(xml_bytes)
        invoice_hash = qr_codes_generator.compute_invoice_hash_base64url_from_bytes(xml_bytes)
        
        url = qr_codes_generator.build_invoice_verification_url(
            nip=seller_nip,
            issue_date=issue_date,
            invoice_hash_base64url=invoice_hash,
            base_url=base_url
        )
        
        import qrcode
        qr = qrcode.QRCode(version=None, error_correction=qrcode.ERROR_CORRECT_L, box_size=5, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except ImportError:
        print("Warning: Could not generate QR code: No module named 'qrcode'. Please run: pip install qrcode[pil]")
        return None
    except Exception as e:
        print(f"Warning: Could not generate QR code: {e}")
        return None

def run_visualization(xml_path, lang="pl", output=None, ksef_no=None, theme="default"):
    if not os.path.exists(xml_path):
        print(f"Error: XML file {xml_path} not found.")
        return False
        
    with open(xml_path, "rb") as f:
        xml_bytes = f.read()
        
    parser_xml = etree.XMLParser(remove_blank_text=True)
    dom = etree.fromstring(xml_bytes, parser_xml)
    
    wariant = detect_fa_version(dom)
    if not wariant:
        print("Error: Could not detect Faktura variant.")
        return False
        
    print(f"Detected FA variant: {wariant} | Theme: {theme} | Lang: {lang}")
    
    # Select stylesheet
    cfg = Config(1)
    
    if theme == "corporate":
        xsl_file = os.path.join(cfg.resources_dir, 'styles', "styl-corporate.xsl")
    else:
        # Default mapping
        if lang == "eng":
            xsl_file = os.path.join(cfg.resources_dir, 'styles', f"styl-fa{wariant}-eng.xsl")
        else:
            xsl_file = os.path.join(cfg.resources_dir, 'styles', f"styl-fa{wariant}.xsl")
        
    if not os.path.exists(xsl_file):
        print(f"Error: Stylesheet {xsl_file} not found.")
        return False
        
    # Generate QR Code and Verification URL
    qr_base64 = get_qr_base64(xml_bytes, ksef_number=ksef_no, base_url=cfg.url)
    verification_url = ""
    if qr_base64:
        # Re-using logic from qr_codes_generator to get the same URL
        from ..utils import qr_codes_generator
        try:
            seller_nip, issue_date = qr_codes_generator.get_seller_nip_and_issue_date_from_invoice_xml_bytes(xml_bytes)
            invoice_hash = qr_codes_generator.compute_invoice_hash_base64url_from_bytes(xml_bytes)
            verification_url = qr_codes_generator.build_invoice_verification_url(
                nip=seller_nip,
                issue_date=issue_date,
                invoice_hash_base64url=invoice_hash,
                base_url=cfg.url
            )
        except:
            pass

    # Transform
    try:
        xslt_dom = etree.parse(xsl_file)
        transform = etree.XSLT(xslt_dom)
        
        # Prepare parameters for XSLT
        params = {
            'lang': etree.XSLT.strparam(lang),
            'ksef-number': etree.XSLT.strparam(ksef_no or ""),
            'qr-code-base64': etree.XSLT.strparam(qr_base64 or ""),
            'verification-url': etree.XSLT.strparam(verification_url),
        }
        
        # Add schema-krajow if needed
        xsd_path = os.path.join(cfg.resources_dir, 'schemas', 'KodyKrajow_v10-0E.xsd')
        params['schema-krajow'] = etree.XSLT.strparam(xsd_path)
        
        newdom = transform(dom, **params)
        html_content = etree.tostring(newdom, pretty_print=True, method="html", encoding="unicode")
        
        # Injection logic (for generic templates that don't handle parameters internally)
        if theme == "default" and qr_base64:
            qr_html = f'<div style="text-align: right; margin-bottom: 20px;"><img src="data:image/png;base64,{qr_base64}" alt="KSeF QR Code" /><br/><small>Weryfikacja KSeF</small></div>'
            html_content = html_content.replace("<body>", f"<body>{qr_html}") if "<body>" in html_content else f"{qr_html}{html_content}"
                
        output_path = output
        if not output_path:
            filename = os.path.basename(xml_path) + ".html"
            # Smart output directory detection
            if "sent" in str(xml_path).lower():
                output_path = os.path.join(cfg.sent_viz, filename)
            elif "received" in str(xml_path).lower():
                output_path = os.path.join(cfg.received_viz, filename)
            else:
                output_path = os.path.join(cfg.reports, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            if not html_content.strip().startswith("<!DOCTYPE"):
                 f.write("<!DOCTYPE html>\n")
            f.write(html_content)
            
        print(f"Success! Visualization saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="KSeF Invoice Visualization Tool")
    parser.add_argument("xml", help="Path to the invoice XML file")
    parser.add_argument("--lang", choices=["pl", "eng"], default="pl", help="Language for visualization")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--theme", default="default", help="Visualization theme (default, corporate)")
    parser.add_argument("--ksef-no", help="KSeF Number (optional)")
    
    args = parser.parse_args()
    run_visualization(args.xml, args.lang, args.output, args.ksef_no, args.theme)

if __name__ == "__main__":
    main()
