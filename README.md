## Folder structure

- tutorial/projects/daily/: daily project info of all known projects
- tutorial/url/url_db.json: all known project urls 
- tutorial/url/daily/: daily urls found
- tutorial/tutorial/spiders/: scraper code

## Variable list
- id: project_id
- url 
- title
- date_created_friendly: date shown on webpage (e.g. 3 days ago)
- date_created_parsed: parsed date in ISO format (failure if empty)
- image
- catagory: see "Catagories" section at the end
- location
- percentage_funded: 0 - 100 (when raised >= goal)
- amount_raised (note currency symbol)
- amount_goal
- description: HTML
- date_url_discovered: date of first discovery of project by crawler

- organizers: the first is main organizer
- beneficiaries

- counts: all counts, empty if the project is closed
- velocity: number recent donations (48h)

- updates
- photos 
- comments: recent, max 10 pages (200 items)
- highest_donations: highest 
- donations: recent, max 10 pages (200 items)

## API list

Donations: https://gateway.gofundme.com/web-gateway/v1/feed/etyn63-medical-bills-and-recovery-for-jin-yut-lew/donations?limit=20&offset=0&sort= [recent / highest]

Comments: https://gateway.gofundme.com/web-gateway/v1/feed/etyn63-medical-bills-and-recovery-for-jin-yut-lew/comments?limit=20&offset=0

Updates: https://gateway.gofundme.com/web-gateway/v1/feed/etyn63-medical-bills-and-recovery-for-jin-yut-lew/updates?limit=20&offset=0

Velocity: https://gateway.gofundme.com/web-gateway/v1/feed/etyn63-medical-bills-and-recovery-for-jin-yut-lew/velocity?type=recent_donations

Counts: https://gateway.gofundme.com/web-gateway/v1/feed/etyn63-medical-bills-and-recovery-for-jin-yut-lew/counts

Photos: https://gateway.gofundme.com/web-gateway/v1/feed/kyivindependent-launch/photos?limit=20&offset=0&photo_type=4

List: https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=1&term=&cid=

## Catagories

["emergency": 2, 
"animals": 3, 
"family": 4, 
"business": 5, 
"event": 6, 
"community": 7, 
"creative": 8, 
"memorial": 9, 
"travel": 10, 
"medical": 11, 
"faith": 12, 
"non-profit": 13, 
"miscellaneous": 15, 
"sports": 16, 
"volunteer": 18, 
"competition": 19, 
"wishes": 20, 
"financial emergency": 344, 
"environment": 342]

The number means catagoryId, which can be ignored.