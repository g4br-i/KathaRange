const axios = require('axios');
const { JSDOM } = require('jsdom');
const { wrapper } = require('axios-cookiejar-support');
const { CookieJar } = require('tough-cookie');

const cookieJar = new CookieJar();

const client = wrapper(axios.create({ jar: cookieJar, withCredentials: true }));

// Specify the IP address of the server to load
client.get('http://192.168.3.10/index.html')
    .then(response => {
        const cookies =  cookieJar.getCookieStringSync("http://192.168.3.10");
        const html = `<script>document.cookie = "${cookies}";</script>\n`+response.data;
        const dom = new JSDOM(html, { 
            runScripts: "dangerously",
            resources: "usable",
            url: "http://192.168.3.10/",
        });
    })
    .catch(err => console.error("Error:", err));
