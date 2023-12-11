const express = require("express");
const { login, cookieString } = require("./Login");
const app = express();
const port = 3001;

app.get("/", async (req, res) => {
  res.send(cookieString(await login()));
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
