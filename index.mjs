import * as cheerio from 'cheerio';
import * as fs from 'fs';

const request = await fetch('https://www.useragents.me');
const document = await request.text();

const $ = cheerio.load(document);

const desktopRegex = new RegExp('^Mozilla\\/5\\.0 \\((Windows NT 1|Macintosh|X11).*$');
const mobileRegex = new RegExp('^Mozilla\\/5\\.0 \\((iPhone|iPad|Android|Linux; Android).*$');

const desktopUserAgents = [];
const mobileUserAgents = [];

$('.ua-textarea').map((_index, el) => {
    const userAgent = $(el).text().trim();
    if (!userAgent.startsWith('Mozilla/5.0 (')) {
        return;
    }

    if (desktopRegex.test(userAgent)) {
        desktopUserAgents.push(userAgent);
    } else if (mobileRegex.test(userAgent)) {
        mobileUserAgents.push(userAgent)
    }
});

const userAgents = {
    desktop: desktopUserAgents.sort(),
    mobile: mobileUserAgents.sort(),
};

const buildDir = './build';
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir);
}
fs.writeFileSync(`${buildDir}/user-agents.json`, JSON.stringify(userAgents, null, 2));
fs.writeFileSync(`${buildDir}/user-agents.min.json`, JSON.stringify(userAgents));
