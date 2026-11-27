import argparse
import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Combina reportes JUnit XML.")
    parser.add_argument("reports_dir", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    report_paths = sorted(
        path
        for path in args.reports_dir.rglob("*.xml")
        if path.resolve() != args.output.resolve()
    )
    suites = []

    for report_path in report_paths:
        root = ET.parse(report_path).getroot()
        if root.tag == "testsuite":
            report_suites = [root]
        elif root.tag == "testsuites":
            report_suites = list(root.iter("testsuite"))
        else:
            raise ValueError(f"Formato JUnit no reconocido: {report_path}")

        for suite in report_suites:
            suite_copy = copy.deepcopy(suite)
            source = report_path.parent.name
            suite_copy.set("name", f"{source}/{suite_copy.get('name', 'tests')}")
            suites.append(suite_copy)

    missing_reports = not suites
    if missing_reports:
        suite = ET.Element("testsuite", name="Pipeline", tests="1", failures="1")
        testcase = ET.SubElement(suite, "testcase", name="Reportes JUnit")
        failure = ET.SubElement(
            testcase,
            "failure",
            message="No se generaron reportes JUnit.",
            type="MissingReports",
        )
        failure.text = "Ninguna suite publicó un archivo XML."
        suites.append(suite)

    report = ET.Element("testsuites")
    for suite in suites:
        report.append(suite)

    test_cases = report.findall(".//testcase")
    failures = report.findall(".//failure")
    errors = report.findall(".//error")
    skipped = report.findall(".//skipped")
    report.set("tests", str(len(test_cases)))
    report.set("failures", str(len(failures)))
    report.set("errors", str(len(errors)))
    report.set("skipped", str(len(skipped)))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(report, space="  ")
    ET.ElementTree(report).write(
        args.output,
        encoding="utf-8",
        xml_declaration=True,
    )
    print(f"XML consolidado: {args.output} ({len(test_cases)} casos)")
    return 1 if missing_reports else 0


if __name__ == "__main__":
    sys.exit(main())
