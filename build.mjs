import { cpSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";

const output = "dist";
const assets = ["index.html", "styles.css", "app.js"];
const dataFiles = [
  "channel_health_analysis.csv",
  "frequency_health_analysis.csv",
  "device_health_analysis.csv",
  "high_risk_recommendations.csv",
  "pre_fec_ber_kpi.csv",
  "och_power_kpi.csv",
  "edfa_kpi.csv",
];

rmSync(output, { recursive: true, force: true });
mkdirSync(output, { recursive: true });

for (const asset of assets) {
  cpSync(asset, join(output, asset));
}

for (const filename of dataFiles) {
  const destination = join(output, "data", "processed", filename);
  mkdirSync(dirname(destination), { recursive: true });
  cpSync(join("data", "processed", filename), destination);
}

console.log(`Static dashboard built in ${output}/ with ${dataFiles.length} verified data files.`);
