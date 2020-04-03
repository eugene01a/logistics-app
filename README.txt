--Note format--
Category:
Every note has a title that describes the items in the list. There should be as few categories as possible.
Examples: Do, Buy, Return

Content:
Every note contains a checklist of items. They can be things to buy/return, or things to do.

sourceApplication
-LogisticsApp

Place:
-All items in the list require me to be at a certain place. The name is what you would type into google map search.
Example: home-depot, walmart

Conditions:
Conditions other than place are specified in tags. Compound tags seperated by dashes (-)
Example: daytime, orange-county, origin-home

--Actions--
add_item(item, category, placeName, conditions):
fetch_items(placeName,conditions)