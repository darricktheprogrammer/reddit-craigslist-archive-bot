<!--
This is a temporary document for the design of the bot. It will contain class/program design details and notes.
-->








Purpose
=======
There are many submissions and comments that link to a craigslist ad for either information, humor or advice. The problem is, craigslist removes ads after 3 months. This is bad for the long tail of Reddit, as people aren't able to garner the context of the post without seeing the ad.

@name alleviates this problem by archiving the ad on imgur and providing a link so that people can see the ad in the future.


Mechanism
=========
The steps for @name to archive an ad are as follows:

1. Poll Reddit for new submissions/comments (using the praw library)
2. check each post for a craigslist url (using regex). Obviously, ignore any posts without it.
3. check if url has already been saved. If so, pull information of of the database instead of making a new album
4. Using the url, download all information from the craigslist ad
	- take a screenshot of the full page (to /tmp folder)
	- get title
	- get text (both source and plain text [if possible])
	- download full size images (to /tmp folder)
5. Extract post number from url (or page actually, if that's easier. it's `post id` on the page)
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
>	Main image | image 1 | image 2 | image 3 | ...
>	
>	original-link


keep a database of previously archived in case of duplicates



UML
===

AdSaver()

Reply()
+post()
