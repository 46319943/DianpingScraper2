const readline = require("readline");
const puppeteer = require("puppeteer");
const puppeteerExtra = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
puppeteerExtra.use(StealthPlugin());

/**
 * 创建一个新浏览器环境和页面
 * @param {*} param0
 * @returns
 */
async function launchPage({ headless = false } = {}) {
  /** @type {puppeteer.Browser} */
  const browser = await puppeteerExtra.launch({
    headless: headless,
    defaultViewport: null,
    args: [
      "--start-maximized", // you can also use '--start-fullscreen'
      // preventing the usual optimizations browsers perform for background tabs and windows.
      // This can be crucial for certain types of automated scripts that require consistent timing and behavior regardless of whether the page is in the foreground or background.
      "--disable-background-timer-throttling",
      "--disable-backgrounding-occluded-windows",
      "--disable-renderer-backgrounding",
    ],
    ignoreDefaultArgs: ["--enable-automation"],
  });
  const page = await browser.newPage();
  return { browser, page };
}

/**
 * 访问页面，自动超时重试
 * @param {import('puppeteer').Page} page
 * @param {*} url
 */
async function pageGoto(page, url) {
  // 访问超时循环
  while (true) {
    try {
      await page.goto(url, {
        timeout: 15000,
        referer: "http://www.dianping.com/",
      });
      break;
    } catch (error) {
      console.log(`time out error occur while goto the ${url}, retrying...`);
      continue;
    }
  }
}

/**
 * 打开登录页面
 * 返回登录后的Cookies
 * @returns
 */
async function login() {
  const { browser, page } = await launchPage();
  await pageGoto(page, "https://account.dianping.com/login");
  await page.waitForSelector("div.login-wrap-prod", {
    timeout: 0,
    hidden: true,
  });
  let loginCookies = await page.cookies();
  await browser.close();
  return loginCookies;
}

function cookieString(cookies) {
  return cookies.map((cookie) => `${cookie.name}=${cookie.value}`).join("; ");
}

module.exports = {
  login,
  cookieString,
};
