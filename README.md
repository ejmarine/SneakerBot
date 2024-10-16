# SneakerBot
 Sneaker prices (retail and resell) webscraper that provides analysis on resell potential

## Main Features

Many sneaker releases, such as Nike Jordans or Adidas’ Yeezys, are produced in limited quantities, creating scarcity. Because of the popularity and exclusivity of these shoes, demand is high for especially low-production and hyped shoe releases. This phenomenon has created an industry where buyers try to purchase multiple of these shoes and resell them for a profit. In addition to reselling, there is demand for tools to more efficently buy shoes and track shoe drops.

This is a script that sends alerts for sneaker drops to users on Discord and SMS. It provides information from multiple sites on the retail price, resell price, and the profitability of each shoe. As resell sites charge fees and shipping, it factors that in, too. The sites it scrapes are Nike SNKRS, Yeezy (Adidas) (depreciated), and Snipes (a popular third party seller). The resell site it gets data from is StockX, one of the most popular sites for sneakerheads. See [Nike](#nike-snkrs-alerts) Alerts, [Yeezy](#yeezy-alerts) Alerts, [Snipes](#snipes-alerts) Alerts, and [SMS](#sms-alerts) Alerts for specific information on these sites. 

### Redesign Goals

Note: As this was written when I was in 10th grade, I didn't follow certain design practices that I would now. Due to this, I plan to rewrite it in the near future.

When scraping Nike, Yeezy, and Snipes, due to a lack of APIs, important information is identified by XPath, which creates issues if the pages are changed in almost any way. I plan to create a solution that dynamically identifies important information to reduce the likelyhood of errors.

Additionally, I plan to clean and split up the code in order to improve readability and ease of debugging.

---

## SMS Alerts

Each text alert provides the cost of the shoe, the optimal shoe to buy, and the estimated profit. To avoid spam, text alerts are only sent for profitable shoes, apposed to Discord alerts, which post every shoe. Texts are sent through the smtplib package and the celluar provider's email to text service. (ex. (123)-456-7890 of verizon goes to 1234567890@vtext.com)

<img src="examples/Text_Example.png" alt="Example of a Text Alert" width="350"/>

---

## Nike [SNKRS](https://www.nike.com/launch) Alerts

Every 24 hours the script requests Nike's upcoming releases in an HTTPS request using Selenium. Identifying every shoe dropping that day, it iterates through each listing and records the shoe's retail price and SKU (stock keeping unit). Then, through an unofficial API, it requests the resell prices on StockX and chooses which size, if any, is the best to purchase.  

<img src="examples/Nike_Example.png" alt="Example of a Nike Alert" width="350"/>

---

## [Snipes](https://www.snipesusa.com/) Alerts

Snipes is a third party seller of athletic and designer wear, mainly Nike. Snipes' schedule is the same as Nike's, so it sends alerts 5 minutes after Nike alerts release. 

<img src="examples/Snipes_Example.png" alt="Example of a Snipes Alert" width="350"/>

---

## Yeezy Alerts

Adidas no longer carries Yeezy merchandise and as such, this feature has been depreciated in version 0.3.3. Before Adidas dropped Yeezy, the script scraped Nike's upcoming releases in an HTTPS request using Selenium & compared the data to StockX, much like the Nike alerts.

<img src="examples/Yeezy_Example.png" alt="Example of a Yeezy Alert" width="350"/>