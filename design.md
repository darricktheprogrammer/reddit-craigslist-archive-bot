<!--
This is a temporary document for the design of the bot. It will contain class/program design details and notes.
-->








Purpose
=======
There are many submissions and comments that link to a craigslist ad for either information, humor or advice. The problem is, craigslist removes ads after 3 months. This is bad for the long tail of Reddit, as people aren't able to understand the context of the post without seeing the ad.

@name alleviates this problem by archiving the ad on imgur and providing a link so that people can see the ad in the future.



Mechanism
=========
The steps for @name to archive an ad are as follows:

1. Poll Reddit for new submissions/comments (using the praw library)
2. check each post for one or more craigslist urls (using regex). Obviously, ignore any posts without it.
5. Extract post number from url
3. check if An archive exists for the ad. If so, pull information of of the database instead of making a new album
4. Using the url, download all information from the craigslist ad
	- take a screenshot of the full page (to /tmp folder)
	- get title
	- get text (both source and plain text [if possible])
	- download full size images (to /tmp folder)
6. Upload to a new imgur album
	- Title = @name archive $postnumber
	- first image = full-page screenshot
	- then all other images
7. delete /tmp files
9. save information to database (actually, do this earlier as an AdSaver class, then have a separate PostReply class?)
8. post reply to original reddit post


reddit reply post will have the title, the text from the craigslist ad (convert html to markdown, so it can be formatted on reddit? can I just use the html?), direct links to each image, and a link to an imgur album with all of this information. The first image will contain a screenshot of the full ad, with the (probably unformatted) text underneath as the description. Imgur album name will be `@name archive $postnumber`




post format:

>	@bleepbloopbottextstuff
>
>	### Title ###
>
>	text of the ad
>
>	Screenshot | image 1 | image 2 | image 3 | ... [or]
>	Screenshot | no images
>	
>	imgur album [$url] | original post [$url]
>	
>	<hr>
>	
>	github [$url]


keep a database of previously archived in case of duplicates


file directory
==============
reddit-craigslist-archive-bot/
	bot/
		run-bot.py
			main()
		bot.py
			Post() <!-- if not covered by praw -->
			Archive()
			Archiver()
			PostFormatter()
			craigslist-bot
		craigslist.py
			scrape_url()
			id_from_url()
			BaseAd()
			CraigslistAd()
			CraigslistAdCache()
		tools.py
			Camera()
tests
[...other files...]


UML
===
scrape_url(url)  => CraigslistAd
id_from_url(url) => string

BaseAd()
+init(id, url, title, body, body_source, images=[])
+id
+url
+title
+body
+body_source
+images


CraigslistAd()  <!-- Represents a craiglist post/ad -->
-validate_image_path(pth)

CraigslistAdCache()
-validate_image_path(pth)


PostFormatter()
-format_markdown_link(text, url) => string
-format_link_list(links) => string
+format(archive) => string


Post() 
<!--
Generic Reddit post, whether submission or comment. This may be covered enough by praw to sublcass praw and peewee's repo to create a Reddit post class that can be saved to the database
-->
+text
+source
+post(reply_to)  <!-- I dont remember praw's api. This may already be covered. -->

Archiver(camera=Camera)
-take_screenshot(url)
+download()
+download_images(CraigslistAd)
+archive(AdCache) => Archive

Archive()  <!-- Represents an imgur album -->
+init(id, url, title, ad, screenshot, images=[])
+id
+url
+title
+ad <!-- Foreign key -->
+screenshot
+images
+upload(AdCache)

Camera()
+take_snapshot(url)




other notes
===========
(Maybe called Clark for CraigList ARK. Saving cl ads from extinction.)

use peewee as an ORM database wrapper so that no SQL is needed. It is lightweight and similar to django-orm, so no extra code or mapping is needed.

In the case of two ads posted, should there be two replies, or one reply with multiple sections?

clark should look for both full urls and href links (i.e. http://indianapolis.craigslist.org/blah/123456789 and [this ad](http://indianapolis.craigslist.org/blah/123456789)). This can just be done with the source of the post, right?


Pseudo code 
==========
While polling 
	extract urls
	For URL in urls found in post
		Get post id from url 
		try
			get existing archive
		On error 
			Download ad data
			archive = Upload to imgur
			Save archive to database
		format reply
		Reply
