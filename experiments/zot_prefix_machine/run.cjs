"use strict";
// Replay to stdout; redirect to a fresh path to retain a new observation.
const fs=require("node:fs");
const path=require("node:path");
const read=name=>fs.readFileSync(path.join(__dirname,name),"utf8");
const M=require("./machine.cjs");
const {campaign}=require("./verify.cjs");
const {keraiaBoundaryCampaign}=require("./keraia-boundary.cjs");
const zot=campaign(M,JSON.parse(read("contract.json")),read("reference-zot.js"));
const keraia=keraiaBoundaryCampaign(JSON.parse(read("keraia-contract.json")));
process.stdout.write(JSON.stringify({zot,keraia},null,2)+"\n");
if(zot.verdict!=="Completed"||keraia.verdict!=="Completed")process.exitCode=1;
