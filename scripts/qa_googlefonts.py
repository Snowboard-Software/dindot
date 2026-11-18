"""Stage the family in Google Fonts' directory layout and run Fontspector."""
from argparse import ArgumentParser
from pathlib import Path
import shutil
import subprocess
import json
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]

if __name__=="__main__":
    p=ArgumentParser(description=__doc__)
    p.add_argument("--fontspector",required=True,type=Path)
    p.add_argument("--font-dir",type=Path,default=ROOT/"fonts/ttf")
    p.add_argument("--report-dir",type=Path,default=ROOT/"documentation/google-fonts")
    p.add_argument("--assert-known-findings",action="store_true",
                   help="Fail CI on new findings; retain the raw unwaived Google Fonts report")
    args=p.parse_args()
    staging=ROOT/".cache/googlefonts/dindot"
    staging.mkdir(parents=True,exist_ok=True)
    for path in staging.glob("*.ttf"):path.unlink()
    for path in args.font_dir.glob("*.ttf"):
        shutil.copy2(path,staging/path.name)
    shutil.copy2(ROOT/"OFL.txt",staging/"OFL.txt")
    dest=args.report_dir.resolve()
    dest.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([str(args.fontspector.resolve()),"-p","googlefonts","-J","4",
        "--timeout","10","--json",str(dest/"fontspector-googlefonts.json"),
        "--ghmarkdown",str(dest/"fontspector-googlefonts.md"),
        *[str(p) for p in sorted(staging.glob("*.ttf"))]])
    if args.assert_known_findings:
        assert result.returncode in (0,1),f"Checker execution failed: {result.returncode}"
        allowed=json.loads((ROOT/"documentation/google-fonts/review-findings.json").read_text())["allowed_findings"]
        report=json.loads((dest/"fontspector-googlefonts.json").read_text())
        counts=Counter()
        for groups in report["results"].values():
            for checks in groups.values():
                for check in checks:
                    for sub in check["subresults"]:
                        if sub["severity"] not in {"WARN","FAIL","ERROR","FATAL"}:continue
                        expected=allowed.get(check["check_id"])
                        assert expected and sub["severity"]==expected["severity"] and sub.get("code")==expected["code"],(check["check_id"],sub)
                        counts[check["check_id"]]+=1
        assert all(count<=allowed[name]["maximum_results"] for name,count in counts.items()),counts
        print("No new QA findings. The raw report retains the unwaived naming, design and serving findings:",dict(counts))
    else:
        raise SystemExit(result.returncode)
