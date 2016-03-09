# Project ReadMe

Project ReadMe is a Python-Flask webapp that empowers users to find library availability across multiple library systems for the books they want to borrow. The user starts by searching for a book by keyword such as title, author or ISBN. The app renders matching search results on a page, allowing the user to select the best matching title. When the user selects a title, the app shows basic book details (such as author, summary, and number of pages), ratings information from Goodreads, and availability of that book across multiple library systems in both map and table formats.

## Technology Stack
* Python
* Flask
* PyQuery
* pytest
* SQLAlchemy
* PostgreSQL
* Javascript
* JQuery
* AJAX
* Bootstrap

## APIs
* Mapbox
* Goodreads

Learn more about the developer:  www.linkedin.com/in/alicepao

## Search Page
Search for a book by keyword such as title, author or ISBN.

1. When the user hits the Search button, a POST request with the search keywords is sent to the server.
2. The server sends a GET request with the search keywords as a parameter to a third-party website WorldCat, which returns HTML content.
3. Using PyQuery, the HTML is parsed for the WorldCat links to each of the result's details pages.
4. The GET request process is repeated for each of the WorldCat details page links, each of which also returns HTML content.
5. Using PyQuery, the HTML is once again parsed for all the necessary book details, including ISBNs, and saved to the database.

The ISBNs are a key component to store in the database, because, from this point onward, the ISBN is the key unique identifier for any book in all third-party API interactions.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/searchpage.png "Project ReadMe Search Page")

## Search Results Page
Based on keyword search, the app renders a page of matching results, pulling the information from the database and linking each result to the appropriate Flask route with the book's ID from the database.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/searchresultspage.png "Project ReadMe Search Results Page")

## Result Details Page
When the user selects a book on the search results page, the details page is rendered, showing general book information, ratings information from the Goodreads API, and the availability of the book at the three county library systems currently supported by the app.

### General Book Information & Ratings Information
The book information and Goodreads ratings information shown on this page are loaded from the database.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/bookdetailspage.png "Project ReadMe Book Details Page")

### Library Availability - Map Format
When the user lands on the book details page, a GET request with the list of relevant ISBNs is sent to multiple county library system APIs for their respective item availability details.

Because each library system represents availability and lack of availability in different ways, back-end functions process each library's availability to normalize the information for rendering in the availability map and table.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/availsmap.png "Project ReadMe Book Details Page - Availability Map")

#### Library Availability - Map Format - Markers
The markers are created by converting the normalized and aggregated availability information into geoJSON format for the Mapbox API to render via Javascript.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/availsmapwithmarkerdiv.png "Project ReadMe Book Details Page - Availability Marker")

#### Library Availability - Map Format - Geolocation Action Button
Using a combination of the built-in browser geolocation API and the Mapbox API, the map re-orients around the user's location and adds it as a blue circle marker on the map.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/geolocationactionbutton.png "Project ReadMe Book Details Page - Geolocation Button")

### Library Availability - Table Format
The library availability is rendered in table format to address some web accessibility concerns in case the map information cannot be viewed.

![alt text](https://github.com/apao/project-readme/blob/master/static/screenshots/availstable.png "Project ReadMe Book Details Page - Availability Table")

## How to Run This App

To be continued...

# Learn More about the Developer

**LinkedIn Profile:** www.linkedin.com/in/alicepao