console.log("Script Loaded");

let host = "http://localhost:9000";

document.body.querySelector("input[type=url]").addEventListener("input", changeHandler);

function changeHandler(event) {
  host = event.target.value;
}

document.body.querySelector("form").addEventListener("submit", submitHandler);

function submitHandler(event) {
  event.preventDefault();
  document.body.querySelector("button").disabled = true;

  const { imptype, csvfile } = Object.fromEntries(new FormData(event.target).entries());

  switch (imptype) {
    case "masters":
      importMasters(csvfile)
        .then((xml) => (document.body.querySelector("pre").innerText = xml))
        .catch((e) => alert(`Error: ${e.message}`))
        .finally(() => (document.body.querySelector("button").disabled = false));
      break;
    case "vouchers":
      importVouchers(csvfile)
        .then((xml) => (document.body.querySelector("pre").innerText = xml))
        .catch((e) => alert(`Error: ${e.message}`))
        .finally(() => (document.body.querySelector("button").disabled = false));
      break;
    default:
      alert(`Invalid import type "${imptype}"`);
      break;
  }
}

async function importMasters(csvfile) {
  const [headers, ...lines] = await toTextCSV(csvfile);
  console.log(headers, lines.length);
  const xml = `
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>All Masters</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <IMPORTDUPS>@@DUPIGNORE</IMPORTDUPS>
            </STATICVARIABLES>
        </DESC>
        <DATA>
            <TALLYMESSAGE>
            ${lines
              .map(
                (line) => `
                <LEDGER NAME="${escSpecial(line[0])}" ACTION="Create">
                    <ADDRESS.LIST TYPE="String">
                        <ADDRESS>${escSpecial(line[7])}</ADDRESS>
                        <ADDRESS>${escSpecial(line[8])}</ADDRESS>
                        <ADDRESS>${escSpecial(line[9])}</ADDRESS>
                        <ADDRESS>${escSpecial(line[10])}</ADDRESS>
                    </ADDRESS.LIST>
                    <NAME>${escSpecial(line[0])}</NAME>
                    <PARENT>${escSpecial(line[1])}</PARENT>
                    <OPENINGBALANCE>${escSpecial(line[2])}</OPENINGBALANCE>
                    <LEDSTATENAME>${escSpecial(line[12])}</LEDSTATENAME>
                    <ISBILLWISEON>${escSpecial(line[3])}</ISBILLWISEON>
                    <GSTREGISTRATIONTYPE>${escSpecial(line[5])}</GSTREGISTRATIONTYPE>
                    <ISGSTAPPLICABLE>${escSpecial(line[4])}</ISGSTAPPLICABLE>
                    <PARTYGSTIN>${escSpecial(line[6])}</PARTYGSTIN>
                    <COUNTRYNAME>${escSpecial(line[11])}</COUNTRYNAME>
                    <COUNTRYOFRESIDENCE>${escSpecial(line[11])}</COUNTRYOFRESIDENCE>
                </LEDGER>
            `
              )
              .join("\n")}
            </TALLYMESSAGE>
        </DATA>
    </BODY>
</ENVELOPE>
`;
  console.log(xml);
  const res = await fetch(host, {
    method: "POST",
    headers: { "Content-type": "text/xml;charset=UTF-8", Accept: "text/xml" },
    body: xml,
    mode: "no-cors"
  });
  const payl = await res.text();
  console.log(res, payl);
  return "XML";
}

async function importVouchers(csvfile) {
  const [headers, ...lines] = await toTextCSV(csvfile);
  console.log(headers, lines.length);
  const xml = `
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
      ${lines
        .map(
          (line) => `
        <TALLYMESSAGE>
          <VOUCHER VCHTYPE="${escSpecial(line[1])}" ACTION="Create">
            <VOUCHERTYPENAME>${escSpecial(line[1])}</VOUCHERTYPENAME>
            <DATE>${escSpecial(line[0])}</DATE>
            <REFERENCEDATE>${escSpecial(line[4])}</REFERENCEDATE>
            <NARRATION>${escSpecial(line[2])}</NARRATION>
            <REFERENCE>${escSpecial(line[3])}</REFERENCE>
            <VOUCHERNUMBER></VOUCHERNUMBER>
            ${getLedgerEntries(
              escSpecial(line[1]),
              [
                [escSpecial(line[7]), escSpecial(line[8])],
                [escSpecial(line[11]), escSpecial(line[12])],
                [escSpecial(line[15]), escSpecial(line[16])],
                [escSpecial(line[19]), escSpecial(line[20])],
                [escSpecial(line[23]), escSpecial(line[24])]
              ],
              [
                [escSpecial(line[5]), escSpecial(line[6])],
                [escSpecial(line[9]), escSpecial(line[10])],
                [escSpecial(line[13]), escSpecial(line[14])],
                [escSpecial(line[17]), escSpecial(line[18])],
                [escSpecial(line[21]), escSpecial(line[22])]
              ]
            )}
          </VOUCHER>
        </TALLYMESSAGE>
      `
        )
        .join("\n")}
      </DATA>
  </BODY>
</ENVELOPE>
`;
  console.log(xml);
  const res = await fetch(host, {
    method: "POST",
    headers: { "Content-type": "text/xml;charset=UTF-8", Accept: "text/xml" },
    body: xml,
    mode: "no-cors"
  });
  const payl = await res.text();
  console.log(res, payl);
  return "XML";
}

function getLedgerEntries(type, credits, debits) {
  switch (type) {
    case "Receipt":
    case "Purchase":
    case "Contra":
    case "Credit Note":
      return (
        credits.map(([name, amount]) => getCreditEntry(name, amount)).join("") +
        debits.map(([name, amount]) => getDebitEntry(name, amount)).join("")
      );
    case "Sales":
    case "Payment":
    case "Journal":
    case "Debit Note":
      return (
        debits.map(([name, amount]) => getDebitEntry(name, amount)).join("") +
        credits.map(([name, amount]) => getCreditEntry(name, amount)).join("")
      );
    default:
      throw new Error(`Unknown Ledger Type ${type}`);
  }
}

function getCreditEntry(name, amount) {
  return `
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>${name}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                        <AMOUNT>${amount}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
  `;
}

function getDebitEntry(name, amount) {
  return `
                    <ALLLEDGERENTRIES.LIST>
                        <LEDGERNAME>${name}</LEDGERNAME>
                        <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                        <AMOUNT>-${amount}</AMOUNT>
                    </ALLLEDGERENTRIES.LIST>
  `;
}

function escSpecial(string = "") {
  return string
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function toTextCSV(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsText(file);
    reader.onerror = (error) => reject(error);
    reader.onload = () =>
      resolve(
        reader.result
          .split("\r\n")
          .slice(0, -1)
          .map((line) => line.split(","))
      );
  });
}
