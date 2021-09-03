# mangabot
Pythonic Discord bot for creating catalouges of users, sources, and mangas for later notification of new releases

## Bots dbs
Most information used by the bot is stored/configured within four .json files:

* users.json
* mangas.json
* sources.json
* quotes.json

Users stores the id, name, and reading list (mangas) of the unique user.

```
{
    "id": 23265...7454655488,
    "name": "SomeAverageJoe#1234",
    "mangas": [
        "My Hero Academia",
        "One Piece",
        "Jujutsu Kaisen",
        "Black Clover",
        "Dr. STONE",
        "My Hero Academia: Vigilantes",
        "The Hunters Guild: Red Hood",
        "Kaiju No. 8",
        "One-Punch Man"
    ]
}
```

Mangas represents the current searchable library within the bot. It contains the name, link, last_updated date, current chapter, and chapter reading link.

```
{
    "name": "Solo Leveling",
    "link": "https://ww2.manganelo.tv/manga/manga-dr980474",
    "last_updated": "Sep 01,2021 - 23:30 PM",
    "current_chapter": "Chapter 165",
    "chapter_link": "https://ww2.manganelo.tv/chapter/manga-dr980474/chapter-165"
}
```

Sources provides the schema used for xpath scraping information necessary to identify the website and paths to manga contents.

```
{
    "name": "Manganelo",
    "link": "https://ww2.manganelo.tv",
    "name_xpath": "/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/h1",
    "last_updated_xpath": "/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div/p[1]/span[2]",
    "chapter_xpath": "/html/body/div[1]/div[3]/div[1]/div[4]/ul/li[1]/a",
    "chapter_link": "/html/body/div[1]/div[3]/div[1]/div[4]/ul/li[1]/a"
}
```

Quotes is used with the owoify library to produce owo-ified quotes.

```
{
"Author": "Chinese proverb",
"Quote": "Talk doesn't cook rice."
}
```

## The commands are used as follows:

To get the current sources, scannable mangas, and reading list:

`@MangaBot list`

Manually issues an update to scan library for new chapters (typically tasked out every 6hrs)

`@MangaBot update`

Adds mangas to the library if source is supported.

`@MangaBot add [LINK/NAME]`

`@MangaBot add [LINK],[LINK],[LINK]....`

Deletes mangas from a users reading list.

`@MangaBot del [NAME]`

`@MangaBot del [NAME],[NAME],[NAME]....`

Allows a user to add users given the correct XPATHs to target.

`@MangaBot source [NAME] [LINK] [xpath_to_name] [xpath_to_date_updated] [xpath_to_chapter/episode]`

This is an example if you were to add support for VIZ Manga:

`@MangaBot source VIZ https://www.viz.com/ /html/body/div[3]/section[1]/div[1]/h2 /html/body/div[3]/section[2]/div/div[2]/div[2]/a/div[1]/table/tbody/tr/td /html/body/div[3]/section[2]/div/div[2]/div[2]/a/div[2]/table/tbody/tr/td[1]/div`

## Compatible Sources

So far the Discord bot has been tested with the following sources:

* https://ww2.manganelo.tv
* https://www.manganelo.tv
* https://manganelo.tv
* https://m.manganelo.com
* https://www.asurascans.com
* https://www.viz.com

And, yes, despite the websites being clones of each other - there are minor differences in the XPATHs that affects the scraping of information from the site.