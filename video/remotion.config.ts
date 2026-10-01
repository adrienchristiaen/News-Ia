import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setCodec("h264");
Config.setCrf(18);
// Sur certaines machines (Linux/CI), pointer vers un Chrome existant : BROWSER=/chemin/vers/chrome
if (process.env.BROWSER) Config.setBrowserExecutable(process.env.BROWSER);
// Chrome « classique » (pas le headless-shell de Remotion) : utile quand BROWSER pointe vers un Chromium récent.
if (process.env.BROWSER) Config.setChromeMode("chrome-for-testing");
