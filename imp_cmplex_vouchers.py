from xml.sax.saxutils import escape
import pandas as pd
import requests

csv_filename = 'complexvouchers.csv'
url = 'http://10.251.74.65:9000'
headers = {"Content-type": "text/xml;charset=UTF-8", "Accept": "text/xml"}


with open(csv_filename, 'r') as f:
    df = pd.read_csv(f, header=0, index_col=False)
    #print(df)

# add helper method for converting column names to lower case and replacing spaces with underscores
df.columns = [c.lower().replace(' ', '_').replace('/','_') for c in df.columns]
print(df.columns)

xml_op = """
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Vouchers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <IMPORTDUPS>@@DUPIGNORE</IMPORTDUPS>
            </STATICVARIABLES>
        </DESC>
        <DATA>
"""

def convert_row(row):

    xml_row = f"""
            <TALLYMESSAGE>
                <VOUCHER VCHTYPE='{escape(row.voucher_type)}' ACTION='Create'>
                    <VOUCHERTYPENAME>{escape(row.voucher_type)}</VOUCHERTYPENAME>
                    <DATE>{row.entry_date}</DATE>
                    <REFERENCEDATE>{row.invoice_date}</REFERENCEDATE>
                    <NARRATION>{escape(row.naration)}</NARRATION>
                    <REFERENCE>{escape(row.supplier_invoice_no)}</REFERENCE>
                    <VOUCHERNUMBER></VOUCHERNUMBER>
"""

    if row.dr_ledger_a != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.dr_ledger_a)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-{row.dr_amount_a}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""

    if row.dr_ledger_b != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.dr_ledger_b)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-{row.dr_amount_b}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""

    if row.dr_ledger_c != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.dr_ledger_c)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-{row.dr_amount_c}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""

    if row.dr_ledger_d != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.dr_ledger_d)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-{row.dr_amount_d}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""

    if row.dr_ledger_e != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.dr_ledger_e)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-{row.dr_amount_e}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""
    
    if row.cr_ledger_a != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.cr_ledger_a)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>{row.cr_amount_a}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""
    
    if row.cr_ledger_b != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.cr_ledger_b)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>{row.cr_amount_b}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""
    
    if row.cr_ledger_c != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.cr_ledger_c)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>{row.cr_amount_c}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""
    
    if row.cr_ledger_d != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.cr_ledger_d)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>{row.cr_amount_d}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""
    
    if row.cr_ledger_e != '-':
        xml_row += f"""
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>{escape(row.cr_ledger_e)}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>{row.cr_amount_e}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
"""

    return (xml_row + """
                </VOUCHER>
            </TALLYMESSAGE>
""")

xml_op += '\n'.join(df.apply(convert_row, axis=1))

xml_op += """
        </DATA>
    </BODY>
</ENVELOPE>
"""

print(xml_op)


response = requests.post(url,data=xml_op, headers=headers)

print(response.text)

# def convert_row(row):
#     if row.voucher_type == 'Receipt' or row.voucher_type == 'Purchase' or row.voucher_type == 'Contra' or row.voucher_type == 'Credit Note': return (f"""<TALLYMESSAGE><VOUCHER VCHTYPE='{escape(row.voucher_type)}' ACTION='Create'><VOUCHERTYPENAME>{escape(row.voucher_type)}</VOUCHERTYPENAME><DATE>{row.entry_date}</DATE><REFERENCEDATE>{row.invoice_date}</REFERENCEDATE><PARTYLEDGERNAME>{escape(row.dr_ledger)}</PARTYLEDGERNAME><NARRATION>{escape(row.naration)}</NARRATION><REFERENCE>{escape(row.supplier_invoice_no)}</REFERENCE><VOUCHERNUMBER></VOUCHERNUMBER><ALLLEDGERENTRIES.LIST><REMOVEZEROENTRIES>No</REMOVEZEROENTRIES><LEDGERFROMITEM>No</LEDGERFROMITEM><ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE><LEDGERNAME>{escape(row.dr_ledger)}</LEDGERNAME><AMOUNT>{row.amount}</AMOUNT></ALLLEDGERENTRIES.LIST><ALLLEDGERENTRIES.LIST><REMOVEZEROENTRIES>No</REMOVEZEROENTRIES><LEDGERFROMITEM>No</LEDGERFROMITEM><ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE><LEDGERNAME>{escape(row.cr_ledger)}</LEDGERNAME><AMOUNT>-{row.amount}</AMOUNT></ALLLEDGERENTRIES.LIST></VOUCHER></TALLYMESSAGE>""")
#     elif row.voucher_type == 'Sales' or row.voucher_type == 'Payment' or row.voucher_type == 'Journal' or row.voucher_type == 'Debit Note': return (f"""<TALLYMESSAGE><VOUCHER VCHTYPE='{escape(row.voucher_type)}' ACTION='Create'><VOUCHERTYPENAME>{escape(row.voucher_type)}</VOUCHERTYPENAME><DATE>{row.entry_date}</DATE><REFERENCEDATE>{row.invoice_date}</REFERENCEDATE><PARTYLEDGERNAME>{escape(row.dr_ledger)}</PARTYLEDGERNAME><NARRATION>{escape(row.naration)}</NARRATION><REFERENCE>{escape(row.supplier_invoice_no)}</REFERENCE><VOUCHERNUMBER></VOUCHERNUMBER><ALLLEDGERENTRIES.LIST><REMOVEZEROENTRIES>No</REMOVEZEROENTRIES><LEDGERFROMITEM>No</LEDGERFROMITEM><ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE><LEDGERNAME>{escape(row.dr_ledger)}</LEDGERNAME><AMOUNT>-{row.amount}</AMOUNT></ALLLEDGERENTRIES.LIST><ALLLEDGERENTRIES.LIST><REMOVEZEROENTRIES>No</REMOVEZEROENTRIES><LEDGERFROMITEM>No</LEDGERFROMITEM><ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE><LEDGERNAME>{escape(row.cr_ledger)}</LEDGERNAME><AMOUNT>{row.amount}</AMOUNT></ALLLEDGERENTRIES.LIST></VOUCHER></TALLYMESSAGE>""")