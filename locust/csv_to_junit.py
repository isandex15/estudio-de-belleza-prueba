import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Uso: csv_to_junit.py <estadisticas.csv> <reporte.xml>")

    csv_path = Path(sys.argv[1])
    xml_path = Path(sys.argv[2])

    with csv_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    request_rows = [
        row
        for row in rows
        if row.get("Type") and row.get("Name") and row["Name"] != "Aggregated"
        and int(row.get("Request Count", 0) or 0) > 0
    ]

    failed_requests = sum(
        int(row.get("Failure Count", 0) or 0)
        for row in request_rows
    )
    suite = ET.Element(
        "testsuite",
        name="Locust",
        tests=str(len(request_rows)),
        failures=str(sum(
            1
            for row in request_rows
            if int(row.get("Failure Count", 0) or 0) > 0
        )),
        errors="0",
        skipped="0",
    )

    for row in request_rows:
        testcase = ET.SubElement(
            suite,
            "testcase",
            classname=row["Type"],
            name=row["Name"],
        )
        failure_count = int(row.get("Failure Count", 0) or 0)
        if failure_count:
            failure = ET.SubElement(
                testcase,
                "failure",
                message=f"{failure_count} de {row['Request Count']} solicitudes fallaron",
                type="LocustRequestFailure",
            )
            failure.text = row["Name"]

    if not request_rows:
        testcase = ET.SubElement(
            suite,
            "testcase",
            classname="Locust",
            name="requests recorded",
        )
        failure = ET.SubElement(
            testcase,
            "failure",
            message="Locust no registró solicitudes",
            type="NoRequests",
        )
        failure.text = "La prueba terminó sin solicitudes registradas."
        suite.set("tests", "1")
        suite.set("failures", "1")

    suite.set("assertions", str(failed_requests))
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(suite, space="  ")
    ET.ElementTree(suite).write(xml_path, encoding="utf-8", xml_declaration=True)

    return 1 if not request_rows or failed_requests else 0


if __name__ == "__main__":
    raise SystemExit(main())
