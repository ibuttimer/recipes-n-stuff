/**
 * Node.js script to run lighthouse tests on project artifacts.
 *
 * Usage: node lighthouse.js -b <site root url> -u <username> -p <password> -r <report> -o <report folder> -t <test folder>
 * Options:
 *       --version     Show version number                                [boolean]
 *   -b, --baseurl     Base url for test
 *                    [string] [default: "https://recipesnstuff.herokuapp.com/"]
 *   -u, --username    Username to use for test                            [string]
 *   -p, --password    Password to use for test                            [string]
 *   -t, --testpath    Test folder *relative to project root*
 *                                                   [string] [default: "doc/test"]
 *   -o, --reportpath  Folder to save reports      [string] [default: "lighthouse"]
 *   -r, --report      Report to run                      [string] [default: "all"]
 *   -s, --show        Show tests in browser, i.e. non-headless mode
 *                                                       [boolean] [default: false]
 *       --help        Show help                                          [boolean]
 *
 * Based on
 *  https://joshuatz.com/posts/2021/using-lighthouse-cli-nodejs/
 *  https://github.com/GoogleChrome/lighthouse/blob/main/docs/recipes/auth/example-lh-auth.js
 *
 * @fileoverview script for running Lighthouse on an authenticated page.
 * See https://github.com/GoogleChrome/lighthouse/tree/main/docs/recipes/auth for more.
 */
import puppeteer from 'puppeteer';
import lighthouse from 'lighthouse';
import lrDesktopConfig from 'lighthouse/lighthouse-core/config/lr-desktop-config.js'
import lrMobileConfig from 'lighthouse/lighthouse-core/config/lr-mobile-config.js'
import esMain from 'es-main';
import yargs from 'yargs/yargs'
import { hideBin } from 'yargs/helpers'
import path from 'path';
import fs from 'fs';
import {
    loginUrl, logoutUrl,
    allViews,
    pre_login_views, preLoginViews,
    post_login_views, postLoginViews,
    usernameTag, listViews
} from './views.js'

// This port will be used by Lighthouse later. The specific port is arbitrary.
const PORT = 8041;

const categoryPerformance = 'performance';
const categoryAccessibility = 'accessibility';
const categoryBestPractices = 'best-practices';
const categorySEO = 'seo';

/** Testing categories */
const categories = [
    // display name        lighthouse report property
    { name: 'Performance', property: categoryPerformance },
    { name: 'Accessibility', property: categoryAccessibility },
    { name: 'Performance', property: categoryBestPractices },
    { name: 'SEO', property: categorySEO },
];
const allCategoryCfg = [
    categoryPerformance, categoryAccessibility, categoryBestPractices, categorySEO
];
const accessibilityBPCfg = [
    categoryAccessibility, categoryBestPractices
];

// https://github.com/GoogleChrome/lighthouse/blob/HEAD/docs/configuration.md
const mainOptions = {
    logLevel: 'info',
    output: 'html',
    onlyCategories: allCategoryCfg,
    port: PORT,
    disableStorageReset: true,
};
const lhConfigs = [
    { name: 'mobile', config: lrMobileConfig },
    { name: 'desktop', config: lrDesktopConfig }
];

const defaultUrl = 'https://recipesnstuff.herokuapp.com/'
const defaultTestPath = 'doc/test';
const defaultReportPath = 'lighthouse';
const rootPath = path.dirname(process.cwd());

/**
 * Report config
 * @param {string} name - report name
 * @param {Array[string]} category - categories to test
 * @param {boolean} login - login required flag; true = needs to be logged in, false = does not need to be logged in
 * @param {string} path - relative path to generated file
 * @returns
 */
const reportCfg = (name, category, login, path) => {
    return { name: name, category: category, login: login, path: path };
};

const allCfgView = view => reportCfg(view.name, allCategoryCfg, view.login, view.path);

/** List of all reports */
const pre_login_cfgs = pre_login_views.map(allCfgView);
const post_login_cfgs = post_login_views.map(allCfgView);
const all_cfgs = pre_login_cfgs.concat(post_login_cfgs);


/**
 * Parse arguments
 * @returns {*}
 */
function parseArgs() {
    return yargs(hideBin(process.argv))
        .option('baseurl', {
            alias: 'b',
            type: 'string',
            description: 'Base url for test',
            default: defaultUrl
        })
        .option('username', {
            alias: 'u',
            type: 'string',
            description: 'Username to use for test'
        })
        .option('password', {
            alias: 'p',
            type: 'string',
            description: 'Password to use for test'
        })
        .option('testpath', {
            alias: 't',
            type: 'string',
            description: 'Test folder *relative to project root*',
            default: defaultTestPath
        })
        .option('reportpath', {
            alias: 'o',
            type: 'string',
            description: 'Folder to save reports',
            default: defaultReportPath
        })
        .option('report', {
            alias: 'r',
            type: 'string',
            description: 'Report to run',
            default: allViews
        })
        .option('show', {
            alias: 's',
            type: 'boolean',
            description: 'Show tests in browser, i.e. non-headless mode',
            default: false
        })
        .option('list', {
            alias: 'l',
            type: 'boolean',
            description: 'List view/view group options',
            default: false
        })
        .help()
        .parse()
}

/**
 * @param {import('puppeteer').Browser} browser
 * @param {string} url
 * @param {object} argv
 */
async function login(browser, url, argv) {
    const usernameSelector = 'input[name="login"]';
    const passwordSelector = 'input[type="password"]';
    const formSelector = '.login';

    if (argv.username == null) {
        throw new Error("'username' argument is required");
    }
    if (argv.password == null) {
        throw new Error("'password' argument is required");
    }

    const page = await browser.newPage();
    await page.goto(new URL(url, argv.baseurl));
    await page.waitForSelector(usernameSelector, {visible: true});

    // Fill in and submit login form.
    const emailInput = await page.$(usernameSelector);
    await emailInput.type(argv.username);
    const passwordInput = await page.$(passwordSelector);
    await passwordInput.type(argv.password);
    await Promise.all([
        page.$eval(formSelector, form => form.submit()),
        page.waitForNavigation(),
    ]);

    await page.close();
}

/**
 * @param {puppeteer.Browser} browser
 * @param {string} url
 * @param {object} argv
 */
async function logout(browser, url, argv) {
    const page = await browser.newPage();
    await page.goto(new URL(url, argv.baseurl));
    await page.close();
}

async function main() {
    const argv = parseArgs();

    if (argv.list) {
        listViews();
        process.exit();
    }

    // Direct Puppeteer to open Chrome with a specific debugging port.
    const browser = await puppeteer.launch({
        args: [`--remote-debugging-port=${PORT}`],
        headless: !argv.show,    // Optional, if you want to see the tests in action.
        slowMo: 50,
    });

    let runList;
    let markdown = '';
    const markdownFile = path.join(rootPath, argv.testpath, argv.reportpath, `results.md`);
    const reportFiles = [];

    const reports = argv.report.toLowerCase();
    if (reports === allViews) {
        runList = all_cfgs;
    } else if (reports === preLoginViews) {
        runList = pre_login_cfgs;
    } else if (reports === postLoginViews) {
        runList = post_login_cfgs;
    } else if (reports === moderatorViews) {
        runList = moderator_cfgs;
    } else {
        runList = all_cfgs.filter(entry => entry.name === reports);
    }

    let isLoggedIn = false;
    for (const running of runList) {

        // config options
        const options = Object.assign({}, mainOptions, {
            onlyCategories: running.category,
        });

        let name = running.name;
        if (running.login) {
            if (!isLoggedIn) {
                // setup the browser session to be logged into site.
                await login(browser, loginUrl, argv);
                isLoggedIn = true;
            }
        }

        let url = path.join(running.path);
        if (url.indexOf(usernameTag) >= 0) {
            url = url.replace(usernameTag, argv.username);
        }
        url = new URL(url, argv.baseurl);

        for (const cfg of lhConfigs) {
            console.log(`Testing ${url}: ${cfg.name}`);

            // Direct Lighthouse to use the same port.
            const runnerResult = await lighthouse(url, options, cfg.config);

            const reportResult = report(runnerResult, options.onlyCategories, name, cfg.name, argv);

            reportFiles.push(reportResult.filename);

            markdown = `${markdown}\n${reportResult.markdown}`;
        }
    }

    // save the generated markdown for report
    fs.writeFileSync(markdownFile, markdown, err => {});

    console.log(`Result reports saved in ${argv.reportpath}`);
    console.log(reportFiles.map(entry => `  ${entry}`).join('\n'));
    console.log(`Report markdown saved in ${markdownFile}`);

    // Direct Puppeteer to close the browser as we're done with it.
    await browser.close();
}

/**
 * Report the results
 * @param {object} runnerResult - lighthouse results
 * @param {Array[object]} categoryCfg - tested categories @see {@link categories}
 * @param {string} name - name of tested resource
 * @param {string} formFactor - form factor used for test
 * @param {object} argv
 * @returns {{filename: string, markdown: string}}
 * @type {string} markdown - markdown text for test report
 * @type {string} filename - report filename
 */
function report(runnerResult, categoryCfg, name, formFactor, argv) {

    // `.lhr` is the Lighthouse Result as a JS object
    console.log(`Report for ${runnerResult.lhr.finalUrl} - ${formFactor}`);

    categories.forEach(category => {
        if (categoryCfg.find(entry => entry === category.property)) {
            console.log(`  ${category.name} score was ${categoryScore(runnerResult, category.property)}`);
        }
    });

    // `.report` is the HTML report as a string
    const reportHtml = runnerResult.report;
    const reportFilename = `${name}-${formFactor}.html`;
    const reportFile = path.join(rootPath, argv.testpath, argv.reportpath, `${name}-${formFactor}.html`);

    fs.writeFileSync(reportFile, reportHtml);

    // generate markdown line for report
    return {
        markdown: shieldsIo(runnerResult, categoryCfg, name, formFactor, reportFile, argv),
        filename: reportFilename
    };
}

/**
 * Generate markdown text for test report
 * @param {object} runnerResult - lighthouse results
 * @param {Array[object]} categoryCfg - tested categories @see {@link categories}
 * @param {string} name - name of tested resource
 * @param {string} formFactor - form factor used for test
 * @param {string} reportFile - relative path to report file
 * @param {object} argv
 * @returns {string} markdown text for test report
 */
function shieldsIo(runnerResult, categoryCfg, name, formFactor, reportFile, argv) {
    let markdown = `| ${titleCase(name)} | ${titleCase(formFactor)} |`;
    categories.forEach(category => {

        let link;

        if (categoryCfg.find(entry => entry === category.property)) {
            const score = categoryScore(runnerResult, category.property);

            link = `![${category.name} ${score}](https://img.shields.io/badge/${category.name}-${score}-${
                score >= 90 ? 'brightgreen' : score >= 50 ? 'orange' : 'red'
            })`;
        } else {
            link = 'n/a';
        }
        markdown += ` ${link} |`
    });

    const url = new URL(path.join(argv.testpath, reportFile), argv.baseurl);

    return `${markdown} [${`${name}-${formFactor}`}](${url}) |`;
}

/**
 * Capitalise first letter
 * @param {string} name
 * @returns {string}
 */
function titleCase(name) {
    return `${name.substring(0, 1).toUpperCase()}${name.substring(1, name.length)}`;
}

/**
 * Extract category score from lighthouse results
 * @param {object} runnerResult - lighthouse results
 * @param {string} property - category property in results
 * @returns
 */
const categoryScore = (runnerResult, property) => {
    return runnerResult.lhr.categories[property].score * 100;
};


if (esMain(import.meta)) {
    main().then();
}

export { login, logout, defaultUrl, defaultTestPath };
