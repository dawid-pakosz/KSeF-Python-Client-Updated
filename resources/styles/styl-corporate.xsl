<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ns="http://crd.gov.pl/wzor/2025/06/25/13775/"
    exclude-result-prefixes="ns">

    <xsl:output method="html" encoding="UTF-8" indent="yes" />

    <!-- Parameters passed from Python -->
    <xsl:param name="lang" select="'pl'" />
    <xsl:param name="ksef-number" select="''" />
    <xsl:param name="qr-code-base64" select="''" />
    <xsl:param name="verification-url" select="''" />

    <!-- Translations -->
    <xsl:variable name="lbl-invoice-no">
        <xsl:choose>
            <xsl:when test="$lang='eng'">Invoice Number</xsl:when>
            <xsl:otherwise>Numer faktury</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="lbl-ksef-no">
        <xsl:choose>
            <xsl:when test="$lang='eng'">KSeF Number:</xsl:when>
            <xsl:otherwise>Numer KSeF:</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="lbl-seller">
        <xsl:choose>
            <xsl:when test="$lang='eng'">Seller</xsl:when>
            <xsl:otherwise>Sprzedawca</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="lbl-buyer">
        <xsl:choose>
            <xsl:when test="$lang='eng'">Buyer</xsl:when>
            <xsl:otherwise>Nabywca</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="lbl-issue-date">
        <xsl:choose>
            <xsl:when test="$lang='eng'">Issue Date:</xsl:when>
            <xsl:otherwise>Data wystawienia:</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="lbl-delivery-date">
        <xsl:choose>
            <xsl:when test="$lang='eng'">Delivery/Execution Date:</xsl:when>
            <xsl:otherwise>Data dokonania/wykonania:</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:template match="/">
        <xsl:apply-templates select="ns:Faktura" />
    </xsl:template>

    <xsl:template match="ns:Faktura">
        <html lang="{$lang}">
            <head>
                <meta charset="utf-8" />
                <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet" />
                <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
                <style>
                    table{border-collapse:collapse;}tr,td,th,thead,tfoot,td div{page-break-inside:avoid;}thead{display:table-header-group;}tfoot{display:table-row-group;}tr{page-break-inside:avoid;height:32px;}html{font-size:22px;}a{text-decoration:none;}.keep-together{page-break-inside:avoid;}.break-before{page-break-before:always;}.break-after{page-break-after:always;}.to-right{float:right;}.to-right--with-margin{margin-left:.5rem;width:100%;}.to-left{float:left;}.to-left--with-margin{margin-right:.5rem;width:100%;}.main-header{width:100%;}.ksef-title{font-family:"Montserrat";font-weight:600;line-height:21px;font-size:1rem;color:#343a40;}.ksef-title-wrapper{width:50%;float:left;}.ksef-title--bold{font-weight:700;}.ksef-title--red{color:#dc0032;}.header-info{float:right;width:100%;}.header-info-wrapper{width:50%;float:right;}.header-info .label-data-info{color:#343a40;display:block;text-align:right;float:left;width:100%;}.header-info .label-data-info--value{font-family:"Open Sans";font-weight:400;font-size:.625rem;line-height:18px;}.header-info .label-data-info--value2{font-family:"Montserrat";font-weight:700;font-size:1.33rem;line-height:35px;overflow-wrap:break-word;word-wrap:break-word;hyphens:auto;white-space:normal;}.header-info .label-data-info--name{font-family:"Open Sans";font-weight:600;font-size:.625rem;margin-right:.1rem;}.header-title{float:left;width:100%;}.header-title--label{font-family:"Montserrat";font-weight:700;font-size:1.125rem;line-height:24px;margin-bottom:.9rem;margin-top:.9rem;display:block;}.section-data{width:100%;float:left;page-break-inside:avoid;}.section-data--margin-top{margin-top:.5rem;}.section-data__header{width:100%;display:block;}.section-data__header--h1{font-family:"Open Sans";font-weight:700;font-size:.75rem;line-height:15px;margin:.5rem 0;float:left;}.section-data__header--table{font-family:"Open Sans";font-weight:600;font-size:.562rem;margin:.5rem 0;}.section-data__wrapper-left{width:50%;float:left;padding-right:.5rem;box-sizing:border-box;}.section-data__wrapper-right{width:50%;float:right;padding-right:.5rem;box-sizing:border-box;}.section-data .label-data-info{color:#343a40;display:block;text-align:left;line-height:16px;}.section-data .label-data-info--text-center{text-align:center;}.section-data .label-data-info--height1{margin-top:.6rem;}.section-data .label-data-info--height2{margin-top:3rem;}.section-data .label-data-info--inline{display:inline;}.section-data .label-data-info--header{font-family:"Open Sans";font-weight:700;font-size:.562rem;line-height:16px;}.section-data .label-data-info--single{font-family:"Open Sans";font-weight:400;font-size:.625rem;line-height:18px;}.section-data .label-data-info--half{width:50%;float:left;padding-right:20px;box-sizing:border-box;}.section-data .label-data-info--half:nth-child(even){float:right;}.section-data .label-data-info--right{margin-top:.5rem;float:right;}.section-data .label-data-info--vertical-space{margin-top:.6rem;margin-bottom:.1rem;}.section-data .label-data-info--bottom-space{margin-bottom:.1rem;}.section-data .label-data-info--name{font-family:"Open Sans";font-weight:600;font-size:.562rem;margin-right:.1rem;}.section-data .label-data-info--name2{font-family:"Open Sans";font-weight:700;font-size:.75rem;margin-right:.1rem;}.section-data .label-data-info--value{font-family:"Open Sans";font-weight:400;font-size:.562rem;overflow-wrap:break-word;word-wrap:break-word;hyphens:auto;white-space:normal;}.section-data .label-data-info--value2{font-family:"Open Sans";font-weight:400;font-size:.75rem;overflow-wrap:break-word;hyphens:auto;white-space:normal;}.section-data .label-data-info--value3{font-family:"Open Sans";font-weight:400;font-size:.562rem;overflow-wrap:break-word;word-wrap:break-word;hyphens:auto;white-space:normal;margin-right:.1rem;}.section-data .label-data-info--italic{font-family:"Open Sans";font-weight:400;font-size:.562rem;font-style:italic;}.section-data__qr-wrapper{float:left;padding-right:1.5rem;padding-top:.3rem;padding-bottom:.5rem;width:207px;}.line-basic{width:100%;margin-top:.9rem;margin-bottom:.5rem;float:left;border:none;height:1px;background-color:#bababa;}.table-basic{margin-top:.5rem;border-collapse:collapse;border-spacing:0;table-layout:fixed;width:100%;}.table-basic__blank_row{height:1.1rem !important;background-color:#fff;}.table-basic--medium-margin{margin-top:.6rem;}.table-basic--large-margin{margin-top:1.1rem;}.table-basic--no-margin{margin-top:0;}.table-basic--auto{width:auto;}.table-basic--wide{width:100%;}.table-basic__header-border{border-bottom:2px solid #343a40;}.table-basic__header{border:1px solid #bababa;padding:8px;text-align:left;background-color:#f6f7fa;font-family:"Open Sans";font-style:normal;font-weight:700;font-size:.5rem;line-height:12px;}.table-basic__header--lp{width:50px;}.table-basic__header--percent80{width:80%;}.table-basic__header--percent67{width:67%;}.table-basic__header--medium-size{min-width:300px;}.table-basic__header--small-txt{text-align:left;font-family:"Open Sans";font-style:normal;font-weight:400;font-size:.5rem;line-height:12px;display:block;}.table-basic__header--nowrap{white-space:nowrap;}.table-basic__cell{border:1px solid #bababa;padding:8px;text-align:left;font-family:"Open Sans";font-style:normal;font-weight:400;font-size:.5rem;line-height:15px;overflow-wrap:break-word;word-wrap:break-word;hyphens:auto;white-space:normal;}.table-basic__cell--to-right{text-align:right;}
                </style>
            </head>
            <body>
                <div class="main-header">
                    <div class="ksef-title-wrapper">
                        <div class="ksef-title">
                            E-faktura została wystawiona przy użyciu 
                            <span class="ksef-title--bold">Krajowego Systemu e-Faktur</span>
                            <span class="ksef-title--red"> (KSeF)</span>
                            zgodnie z obowiązującymi przepisami prawa.
                        </div>
                    </div>
                    <div class="header-info-wrapper">
                        <div class="header-info">
                            <span class="label-data-info">
                                <span class="label-data-info--value"><xsl:value-of select="$lbl-invoice-no" /></span>
                            </span>
                            <span class="label-data-info">
                                <span class="label-data-info--value2"><xsl:value-of select="ns:Fa/ns:P_2" /></span>
                            </span>
                            <span class="label-data-info">
                                <span class="label-data-info--value">Faktura podstawowa</span>
                            </span>
                            <xsl:if test="$ksef-number != ''">
                                <span class="label-data-info">
                                    <span class="label-data-info--name"><xsl:value-of select="$lbl-ksef-no" /></span>
                                    <span class="label-data-info--value"><xsl:value-of select="$ksef-number" /></span>
                                </span>
                            </xsl:if>
                        </div>
                    </div>
                </div>

                <!-- Seller & Buyer -->
                <div class="section-data">
                    <div class="line-basic"></div>
                    <div class="section-data__wrapper-left">
                        <span class="section-data__header section-data__header--h1"><xsl:value-of select="$lbl-seller" /></span>
                        <span class="label-data-info">
                            <span class="label-data-info--name">NIP:</span>
                            <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot1/ns:DaneIdentyfikacyjne/ns:NIP" /></span>
                        </span>
                        <span class="label-data-info">
                            <span class="label-data-info--name">Nazwa:</span>
                            <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot1/ns:DaneIdentyfikacyjne/ns:Nazwa" /></span>
                        </span>
                        <span class="label-data-info label-data-info--vertical-space">
                            <span class="label-data-info--header">Adres</span>
                        </span>
                        <span class="label-data-info">
                            <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot1/ns:Adres/ns:AdresL1" /></span>
                        </span>
                    </div>
                    <div class="section-data__wrapper-right">
                        <span class="section-data__header section-data__header--h1"><xsl:value-of select="$lbl-buyer" /></span>
                        <xsl:if test="ns:Podmiot2/ns:DaneIdentyfikacyjne/ns:NIP">
                            <span class="label-data-info">
                                <span class="label-data-info--name">NIP:</span>
                                <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot2/ns:DaneIdentyfikacyjne/ns:NIP" /></span>
                            </span>
                        </xsl:if>
                        <xsl:if test="ns:Podmiot2/ns:DaneIdentyfikacyjne/ns:NrVatUE">
                             <span class="label-data-info">
                                <span class="label-data-info--name">VAT-UE:</span>
                                <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot2/ns:DaneIdentyfikacyjne/ns:NrVatUE" /></span>
                            </span>
                        </xsl:if>
                        <span class="label-data-info">
                            <span class="label-data-info--name">Nazwa:</span>
                            <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot2/ns:DaneIdentyfikacyjne/ns:Nazwa" /></span>
                        </span>
                        <span class="label-data-info label-data-info--vertical-space">
                            <span class="label-data-info--header">Adres</span>
                        </span>
                        <span class="label-data-info">
                            <span class="label-data-info--value"><xsl:value-of select="ns:Podmiot2/ns:Adres/ns:AdresL1" /></span>
                        </span>
                    </div>
                </div>

                <!-- Dates -->
                <div class="section-data">
                    <div class="line-basic"></div>
                    <span class="section-data__header section-data__header--h1">Szczegóły</span>
                    <span class="label-data-info label-data-info--half">
                        <span class="label-data-info--name"><xsl:value-of select="$lbl-issue-date" /></span>
                        <span class="label-data-info--value"><xsl:value-of select="ns:Fa/ns:P_1" /></span>
                    </span>
                    <xsl:if test="ns:Fa/ns:P_6">
                        <span class="label-data-info label-data-info--half">
                            <span class="label-data-info--name"><xsl:value-of select="$lbl-delivery-date" /></span>
                            <span class="label-data-info--value"><xsl:value-of select="ns:Fa/ns:P_6" /></span>
                        </span>
                    </xsl:if>
                </div>

                <!-- Items -->
                <div class="section-data">
                    <div class="line-basic"></div>
                    <span class="section-data__header section-data__header--h1">Pozycje</span>
                    <table class="table-basic table-basic--wide">
                        <thead>
                            <tr>
                                <th class="table-basic__header table-basic__header--lp">Lp.</th>
                                <th class="table-basic__header">Opis</th>
                                <th class="table-basic__header">Cena jedn.</th>
                                <th class="table-basic__header">Ilość</th>
                                <th class="table-basic__header">Jm.</th>
                                <th class="table-basic__header">Stawka VAT</th>
                                <th class="table-basic__header">Wartość netto</th>
                            </tr>
                        </thead>
                        <tbody>
                            <xsl:for-each select="ns:Fa/ns:FaWiersz">
                                <tr>
                                    <td class="table-basic__cell"><xsl:value-of select="ns:NrWierszaFa" /></td>
                                    <td class="table-basic__cell"><xsl:value-of select="ns:P_7" /></td>
                                    <td class="table-basic__cell table-basic__cell--to-right"><xsl:value-of select="ns:P_9A" /></td>
                                    <td class="table-basic__cell table-basic__cell--to-right"><xsl:value-of select="ns:P_8B" /></td>
                                    <td class="table-basic__cell"><xsl:value-of select="ns:P_8A" /></td>
                                    <td class="table-basic__cell"><xsl:value-of select="ns:P_12" /></td>
                                    <td class="table-basic__cell table-basic__cell--to-right"><xsl:value-of select="ns:P_11" /></td>
                                </tr>
                            </xsl:for-each>
                        </tbody>
                    </table>
                    <div class="label-data-info label-data-info--right">
                        <span class="label-data-info--name2">Kwota należności ogółem:</span>
                        <span class="label-data-info--value2"><xsl:value-of select="ns:Fa/ns:KodWaluty" /><xsl:value-of select="ns:Fa/ns:P_15" /></span>
                    </div>
                </div>

                <!-- Footer / QR -->
                <div class="section-data">
                    <div class="line-basic"></div>
                    <xsl:if test="$qr-code-base64 != ''">
                         <div class="section-data__qr-wrapper">
                            <img height="207" alt="QR Code" src="data:image/png;base64,{$qr-code-base64}" />
                            <span class="label-data-info label-data-info--height1 label-data-info--text-center">
                                <span class="label-data-info--name"><xsl:value-of select="$ksef-number" /></span>
                            </span>
                        </div>
                        <div style="float: left; width: 70%;">
                            <div class="label-data-info label-data-info--height2">
                                <span class="label-data-info--name">Weryfikacja faktury:</span>
                            </div>
                            <div class="label-data-info label-data-info--height1">
                                <span class="label-data-info--value">
                                    <a href="{$verification-url}"><xsl:value-of select="$verification-url" /></a>
                                </span>
                            </div>
                        </div>
                    </xsl:if>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
