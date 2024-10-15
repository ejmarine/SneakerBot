import discord
import os
import time
from discord.ext import commands
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from pytz import HOUR, timezone
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium import webdriver
from random import randrange
import urllib3
import json
import requests
import cloudscraper
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent
from bs4 import BeautifulSoup
import smtplib

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED'
)
urllib3.disable_warnings()

months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
scraper = cloudscraper.create_scraper()

algolia = {
    "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
    "x-algolia-application-id": "XW7SBCT9V6",
    "x-algolia-api-key": "6b5e76b49705eb9f51a06d3c82f7acee"
}

emailList = open("email.txt", 'r').read().split("\n")

tz = timezone('US/Eastern')

driver = uc.Chrome()
options = uc.ChromeOptions()

chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

activity = discord.Game(name="Sniping Sneakers")
bot = commands.Bot(command_prefix='+', activity=activity)
bot.remove_command('help')
load_dotenv()
TOKEN = os.getenv('TOKEN')

channel = bot.get_channel(914940576506449941)


def getShoeInfo(args, embed, msrp, emailMessage):
    try:
        # StockX
        args = args + "%20"
        json_string = json.dumps(
            {"params": f"query={args}&hitsPerPage=10&facets=*"})
        byte_payload = bytes(json_string, 'utf-8')
        with requests.Session() as session:
            r = session.post("https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
                             params=algolia, data=byte_payload, timeout=10)
            results = r.json()["hits"][0]
            apiurl = f"https://stockx.com/api/products/{results['url']}?includes=market,360&currency=USD"
            header = {
                'accept': '*/*',
                'accept-encoding': 'deflate, gzip',
                'accept-language': 'en-US,en;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
            }
            response = requests.get(apiurl, verify=False, headers=header)

        prices = response.json()
        general = prices['Product']
        market = prices['Product']['market']
        sizes = prices['Product']['children']
        img = prices['Product']['media']['thumbUrl']
        stockX = "https://stockx.com/" + prices['Product']['shortDescription']

        try:
            img = img.split(",")[0]
            embed.set_thumbnail(url=img)
        except:
            img = "https://media.discordapp.net/attachments/914954008215584778/920710588915654696/unknown.png?width=1016&height=1018"
            embed.set_thumbnail(url=img)

        bidasks = ''
        sizeShoe = []
        bids = []
        asks = []

        msrp = float(msrp) * 1.06

        for size in sizes:
            if len(bidasks) + len(f"Size {sizes[size]['shoeSize']} | Low Ask ${sizes[size]['market']['lowestAsk']} | High Bid ${sizes[size]['market']['highestBid']}\n") < 1024:
                bidasks += f"Size {sizes[size]['shoeSize']} | Low Ask ${sizes[size]['market']['lowestAsk']} | High Bid ${sizes[size]['market']['highestBid']}\n"
                sizeShoe.append(sizes[size]['shoeSize'])
                asks.append(sizes[size]['market']['lowestAsk'])
                bids.append(sizes[size]['market']['highestBid'])

        for s in range(len(sizeShoe)):
            sizeShoe[s] = sizeShoe[s].replace("W", "")
            sizeShoe[s] = sizeShoe[s].replace("K", "")
            sizeShoe[s] = sizeShoe[s].replace("Y", "")
            sizeShoe[s] = sizeShoe[s].replace("C", "")

        for i in range(len(sizeShoe)-1, -1, -1):
            if float(sizeShoe[i]) < 6 or float(sizeShoe[i]) > 12.5:
                sizeShoe.pop(i)
                asks.pop(i)
                bids.pop(i)

        highBid = max(bids)
        highAsk = max(asks)

        bidProfit = round((highBid * .875) - msrp, 2)
        bidSize = sizeShoe[bids.index(highBid)]
        askProfit = round((highAsk * .875) - msrp, 2)
        askSize = sizeShoe[asks.index(highAsk)]

        bidPercent = str(round((bidProfit / msrp) * 100, 3))
        askPercent = str(round((askProfit / msrp) * 100, 3))

        # GOAT

        if bidProfit > 70:
            buy = "Quick Buy"
        elif bidProfit > 40:
            buy = "Buy"
        else:
            buy = "Don't Buy"

        if bidProfit < 0:
            bidProfit = str(round(bidProfit, 2)).replace("-", "-$")
        else:
            bidProfit = "$" + str(round(bidProfit, 2))
        if askProfit < 0:
            askProfit = str(round(askProfit, 2)).replace("-", "-$")
        else:
            askProfit = "$" + str(round(askProfit, 2))

        # Goat
        if "Don't Buy" not in buy:
            try:
                smtp = smtplib.SMTP('smtp.office365.com', 587)
                smtp.ehlo()
            except:
                print('email went wrong')

            try:
                smtp.starttls()  # tell server we want to communicate with TLS encryption
                smtp.login(os.getenv('SMTP_EMAIL'), os.getenv('SMTP_PASS'))
            except:
                print('login failed')

            emailMessage += "retails for $" + \
                str(round(msrp / 1.06, 2)) + ", buy size " + \
                str(bidSize) + " for " + bidProfit + " profit"

            for email in emailList:
                if len(email) >= 3:
                    try:
                        smtp.sendmail(os.getenv('SMTP_EMAIL'), email,
                                      "From: " + os.getenv('SMTP_EMAIL') + "\nTo: " + email + "\nDate: 7/22/22\n\n" + emailMessage)
                    except Exception as e:
                        print("email to " + str(email) +
                              ' failed because ' + str(e))

            try:
                smtp.quit()  # finally, don't forget to close the connection
            except:
                print('quit failed')

        embed.add_field(name="Stock Cost", value="MSRP: $" + str(round(msrp / 1.06, 2)) +
                        "\n" + "Plus Tax: $" + str(round(msrp, 2)), inline=False)
        embed.add_field(name="Resell Profit to Stockx", value="Shoe Size: " + str(bidSize) + "\n" + "Resells For: $" + str(
            round(highBid * .875, 2)) + "\n" + "Profit Margin: " + str(bidProfit) + " (" + bidPercent + "%) ", inline=False)
        #embed.add_field(name="Resell to Highest Ask", value= "Shoe Size: " + str(askSize) + "\n" + "Resells For: $" + str(round(highAsk * .875, 2)) + "\n" + "Profit Margin: " + str(askProfit) + " (" + askPercent + "%) ", inline=False)
        embed.add_field(name="Buy?", value=buy, inline=False)
        linkVal = "[Stockx](%s), [GOAT](%s)" % (stockX, "goat.com")
        embed.add_field(name="Reseller:",  value=linkVal, inline=False)
        return embed
    except Exception as e:
        print(e)
        return "error"


@bot.command()
async def up(ctx, args):
    await ctx.send("Bot is up " + args)


@bot.command()
async def start(ctx):
    await ctx.send("started")
    started = False

    while True:
        date = datetime.now(tz)

        # Nike
        if date.hour == 9 and date.minute == 25 and started == False:
            try:
                print("started nike")
                print(date)
                started = True
                ctx = bot.get_channel(914940112893276160)

                software_names = [SoftwareName.CHROME.value]
                hardware_type = [HardwareType.MOBILE__PHONE]
                user_agent_rotator = UserAgent(
                    software_names=software_names, hardware_type=hardware_type)

                headers = {
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-GB,en;q=0.9',
                    'appid': 'com.nike.commerce.snkrs.web',
                    'content-type': 'application/json; charset=UTF-8',
                    'dnt': '1',
                    'nike-api-caller-id': 'nike:snkrs:web:1.0',
                    'origin': 'https://www.nike.com',
                    'referer': 'https://www.nike.com/',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'user-agent': user_agent_rotator.get_random_user_agent()
                }

                items = []

                anchor = 0
                while anchor < 160:
                    url = f'https://api.nike.com/product_feed/threads/v3/?anchor={anchor}&count=50&filter=marketplace%28US%29&filter=language%28en%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29'
                    html = requests.get(url=url, timeout=20,
                                        verify=False, headers=headers)
                    output = json.loads(html.text)

                    # Stores details in array
                    for item in output['objects']:
                        items.append(item)

                    anchor += 50

                dat = str(datetime.now(tz).year) + "-"

                if len(str(datetime.now(tz).month)) == 1:
                    dat += "0" + str(datetime.now(tz).month) + "-"
                else:
                    dat += str(datetime.now(tz).month) + "-"
                if len(str(datetime.now(tz).day)) == 1:
                    dat += "0" + str(datetime.now(tz).day)
                else:
                    dat += str(datetime.now(tz).day)

                print(dat)

                shoeInfo = []

                for item in items:
                    try:
                        if items.index(item) > 0 and item == items[items.index(item)-1]:
                            print("passed")
                            pass
                        else:
                            if item['productInfo'][0]['merchProduct']['commercePublishDate'].split("T")[0] == dat:
                                print("date")
                                try:
                                    if len(item['productInfo']) > 1:
                                        for n in range(0, len(item['productInfo'])):
                                            shoeInfo.append([months[datetime.now(
                                                tz).month] + " " + str(datetime.now(tz).day)])
                                            shoeInfo[len(shoeInfo) -
                                                     1].append(item['publishedContent']['properties']['title'])
                                            shoeInfo[len(shoeInfo)-1].append(item['publishedContent']
                                                                             ['nodes'][0]['properties']['title'] +
                                                                             "\n" +
                                                                             item['productInfo']
                                                                             [n]['productContent']['subtitle'])
                                            shoeInfo[len(shoeInfo) -
                                                     1].append("https://www.nike.com/launch/t/" + item['publishedContent']['properties']['seo']['slug'])
                                            shoeInfo[len(shoeInfo)-1].append(item['productInfo']
                                                                             [n]['merchPrice']['msrp'])
                                            shoeInfo[len(shoeInfo)-1].append(item['productInfo']
                                                                             [n]['merchProduct']['styleColor'])
                                    else:
                                        shoeInfo.append([months[datetime.now(
                                            tz).month] + " " + str(datetime.now(tz).day)])
                                        shoeInfo[len(shoeInfo) -
                                                 1].append(item['publishedContent']['properties']['title'])
                                        shoeInfo[len(shoeInfo)-1].append(item['publishedContent']
                                                                         ['nodes'][0]['properties']['title'])
                                        shoeInfo[len(shoeInfo) -
                                                 1].append("https://www.nike.com/launch/t/" + item['publishedContent']['properties']['seo']['slug'])
                                        shoeInfo[len(shoeInfo)-1].append(item['productInfo']
                                                                         [0]['merchPrice']['msrp'])
                                        shoeInfo[len(shoeInfo)-1].append(item['productInfo']
                                                                         [0]['merchProduct']['styleColor'])
                                except Exception as e:
                                    print(e)
                    except Exception as e:
                        pass

                for s in range(len(shoeInfo)-1, -1, -1):
                    if "Apparel Collection" in shoeInfo[s][2] or "Apparel + Accessories" in shoeInfo[s][2] or "Dresses + Skirts" in shoeInfo[s][2]:
                        shoeInfo.pop(s)

                print(shoeInfo)

                # What shoeInfo might look like: [['24', "Women's Dunk Low ", 'Vintage Green ', 'https://www.nike.com/launch/t/womens-dunk-low-vintage-green', '110', 'DQ8580-100']]
                if len(shoeInfo) == 0:
                    embed = discord.Embed(
                        title="Looks like nothing's on sale right now.", description="Enjoy the day off!", color=0x3498db)
                    await ctx.send(embed=embed)
                else:
                    for info in shoeInfo:
                        if len(info) == 0 and len(shoeInfo) == 0:
                            embed = discord.Embed(
                                title="Looks like nothing's on sale right now.", description="Enjoy the day off!", color=0x3498db)
                            await ctx.send(embed=embed)
                            break
                        else:
                            embed = discord.Embed(
                                title=info[1], description=info[2] + "\nDrops " + info[0] + "\nSKU: " + info[5], color=0x3498db, url=info[3])
                            emailMessage = info[1] + " " + \
                                info[2].replace("\n", " ") + \
                                " drops today at 10am, "
                            embed = getShoeInfo(
                                info[5], embed, info[4], emailMessage)
                            if embed != 'error':
                                await ctx.send(embed=embed)
                        time.sleep(10)
                print(date)
            except:
                await ctx.send(embed=discord.Embed(title="An error has occured.", description="Please contact an administrator"))
        # Snipes
        elif date.hour == 9 and date.minute == 20 and started == False:
            try:

                print("started snipes")
                print(date)
                started = True
                ctx = bot.get_channel(1011101373431033946)
                driver = uc.Chrome(options=options)
                driver.get("https://www.snipesusa.com/new-arrivals")
                time.sleep(3)
                html = driver.find_elements(By.CLASS_NAME, "grid-tile.product")
                print(len(html))
                shoeinfo = []
                for i in html:
                    dic = json.loads(i.get_attribute('data-impressiondata'))
                    try:
                        print(i.find_element(By.CLASS_NAME, 'tile-brand').text)
                        if i.find_element(By.CLASS_NAME, 'tile-brand').text == 'Nike' or i.find_element(By.CLASS_NAME, 'tile-brand').text == 'Jordan' or i.find_element(By.CLASS_NAME, 'clock-timer.hours').text == "0":
                            shoeinfo.append([str(datetime.now(tz).day), dic['name'], "", i.find_element(
                                By.TAG_NAME, 'a').get_attribute('href'), dic['price'], dic['productVariant']])
                    except Exception as e:
                        pass
                if len(shoeinfo) != 0:
                    for info in shoeinfo:
                        if len(info) == 0:
                            pass
                        else:
                            embed = discord.Embed(
                                title=info[1], description="Drops " + info[0] + "\nSKU: " + info[5], color=0x3498db, url=info[3])
                            emailMessage = info[1] + " " + \
                                info[2].replace("\n", " ") + \
                                " drops today at 10am, "
                            embed = getShoeInfo(
                                info[5], embed, info[4], emailMessage)
                            if embed != 'error':
                                await ctx.send(embed=embed)
                        time.sleep(5)
            except:
                await ctx.send(embed=discord.Embed(title="An error has occured.", description="Please contact an administrator"))

        if (date.hour == 9 and date.minute == 30) or (date.hour == 8 and date.minute == 30) or (date.hour == 9 and date.minute == 24):
            started = False


bot.run(TOKEN)
