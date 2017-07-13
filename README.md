# Label Manager
SES-imagotag's Odoo module for retailers.
====================================

This Module is used to manage ESLs (electronic shelf labels)
------------------------------------

![alt text](http://cdn-static.boursier.com/illustrations/photos/l_ses2.jpg)

To use this module, you need to have ESLs  you can buy by contacting us on http://www.ses-imagotag.com/contact/
-----------------------

To Configure the module :
------------------------
The first thing you have to do is to set the ip address of the imagotag server in configuration menu of the module.
After having your imagotag server up, you can :
- Add ESLs (that registers automatically on the imagotag server),
- Add templates (that has to be registered first on imagotag server),

Then, in configuration menu of the module, you will have to : 
- Link the right Point of Sale where the labels are settled. This link is used to get the correct prices of the products 
- Link the module to a 'staff' or 'management' template that will be displayed on every label once the store closes.
- Write the domain or the ip-address:8069 of the odoo server if you want to test urls and QRCodes

After all this done, you need to configure scheduled actions that has been generated by the module.
You have to go in Settings/Technical/Automation/ScheduledAction tab, There are 4 of them :
- Update ESLs (When store opens) that sends data to the labels when store opens
- Update ESLs (When store closes) that sends data to the labels when store closes
- Switch pages ESLs (When store opens) that make the labels change to the template they are normally linked to.
- Switch pages ESLs (When store closes) that make the labels change to the 'staff' template linked in the configuration menu.

To configure all these Scheduled Actions, you just need to set the time of the day store closes and opens on switch pages

To get latest information on ESLs, set the time of 'Update ESLs' 5-10 minutes before the switch page.


Now that your module is fully configured, you can start using it.

Start having fun : Link products
-----------------------
Two ways to link your products to your registered labels :
- From the labels, when you're on the page of the label, click on Action-->Create/Modify Matching and add items to the list of products.
  After this, you need to select a template that handle your label (normally you can't select a template that can't handle it).
- From the products, when you've selected one or many products in the list of products (you can also do it from the form of the product)
  , click on Action-->Create Matching. You'll then have a list of your labels, just click on new. A first template will be selected 
  but you can still change it.
  
To test if it's working, run manually the scheduled actions Update ESLs and Switch Pages.

Send Images to labels
---------------------

To send additionnal images to the labels, for now you'll be provided a template that will display the additionnal picture you can add 
on the matching page of the label.
This additionnal image can be used by other templates to render better.
