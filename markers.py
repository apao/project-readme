import tempmvp

def create_markers_by_item_avail(isbn):
    """Create markers for Mapbox map based on searching isbn for library availability."""

    feature_dict = {}
    sccl_avail = tempmvp.get_sccl_availability(isbn)

    for avail in sccl_avail:
        if "Due" not in avail['status']:
            avail_dict = dict(
                                  "type": "Feature",
                                  "properties": {
                                    "description": "<div class=\"marker-title\">%s</div><p>%s | %s | %s</p>",
                                    "marker-symbol": %s
                                  },
                                  "geometry": {
                                    "type": "Point",
                                    "coordinates": [%f,%f]
                                  }
                              ) % ('Branch', 'Test', 'TestA', 'TestB', 'library', -77.007481, 38.876516)


def normalize_sccl_availability(list_of_dicts):
    # branch_name
    # call_no
    # status
    # total_num_of_copies
    # long_lat_of_branch (get from hardcoded dictionary or database)
    pass

def normalize_sfpl_availability(list_of_dicts):
    pass

def normalize_smcl_availability(list_of_dicts):
    pass




        dict_of_status_details['branch_name'] = branch_name_and_copies[0].rstrip()
        dict_of_status_details['num_of_copies'] = int(branch_name_and_copies[1])
        dict_of_status_details['branch_section'] = list_of_status_details[1]
        dict_of_status_details['call_no'] = list_of_status_details[2]
        dict_of_status_details['status'] = list_of_status_details[3]


markers = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Make it Mount Pleasant</div><p><a href=\"http://www.mtpleasantdc.com/makeitmtpleasant\" target=\"_blank\" title=\"Opens in a new window\">Make it Mount Pleasant</a> is a handmade and vintage market and afternoon of live entertainment and kids activities. 12:00-6:00 p.m.</p>",
                "marker-symbol": "theatre"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.038659, 38.931567]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Mad Men Season Five Finale Watch Party</div><p>Head to Lounge 201 (201 Massachusetts Avenue NE) Sunday for a <a href=\"http://madmens5finale.eventbrite.com/\" target=\"_blank\" title=\"Opens in a new window\">Mad Men Season Five Finale Watch Party</a>, complete with 60s costume contest, Mad Men trivia, and retro food and drink. 8:00-11:00 p.m. $10 general admission, $20 admission and two hour open bar.</p>",
                "marker-symbol": "theatre"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.003168, 38.894651]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Big Backyard Beach Bash and Wine Fest</div><p>EatBar (2761 Washington Boulevard Arlington VA) is throwing a <a href=\"http://tallulaeatbar.ticketleap.com/2012beachblanket/\" target=\"_blank\" title=\"Opens in a new window\">Big Backyard Beach Bash and Wine Fest</a> on Saturday, serving up conch fritters, fish tacos and crab sliders, and Red Apron hot dogs. 12:00-3:00 p.m. $25.grill hot dogs.</p>",
                "marker-symbol": "bar"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.090372, 38.881189]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Ballston Arts & Crafts Market</div><p>The <a href=\"http://ballstonarts-craftsmarket.blogspot.com/\" target=\"_blank\" title=\"Opens in a new window\">Ballston Arts & Crafts Market</a> sets up shop next to the Ballston metro this Saturday for the first of five dates this summer. Nearly 35 artists and crafters will be on hand selling their wares. 10:00-4:00 p.m.</p>",
                "marker-symbol": "art-gallery"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.111561, 38.882342]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Seersucker Bike Ride and Social</div><p>Feeling dandy? Get fancy, grab your bike, and take part in this year's <a href=\"http://dandiesandquaintrelles.com/2012/04/the-seersucker-social-is-set-for-june-9th-save-the-date-and-start-planning-your-look/\" target=\"_blank\" title=\"Opens in a new window\">Seersucker Social</a> bike ride from Dandies and Quaintrelles. After the ride enjoy a lawn party at Hillwood with jazz, cocktails, paper hat-making, and more. 11:00-7:00 p.m.</p>",
                "marker-symbol": "bicycle"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.052477, 38.943951]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Capital Pride Parade</div><p>The annual <a href=\"http://www.capitalpride.org/parade\" target=\"_blank\" title=\"Opens in a new window\">Capital Pride Parade</a> makes its way through Dupont this Saturday. 4:30 p.m. Free.</p>",
                "marker-symbol": "star"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.043444, 38.909664]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Muhsinah</div><p>Jazz-influenced hip hop artist <a href=\"http://www.muhsinah.com\" target=\"_blank\" title=\"Opens in a new window\">Muhsinah</a> plays the <a href=\"http://www.blackcatdc.com\">Black Cat</a> (1811 14th Street NW) tonight with <a href=\"http://www.exitclov.com\" target=\"_blank\" title=\"Opens in a new window\">Exit Clov</a> and <a href=\"http://godsilla.bandcamp.com\" target=\"_blank\" title=\"Opens in a new window\">Gods’illa</a>. 9:00 p.m. $12.</p>",
                "marker-symbol": "music"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.031706, 38.914581]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">A Little Night Music</div><p>The Arlington Players' production of Stephen Sondheim's  <a href=\"http://www.thearlingtonplayers.org/drupal-6.20/node/4661/show\" target=\"_blank\" title=\"Opens in a new window\"><em>A Little Night Music</em></a> comes to the Kogod Cradle at The Mead Center for American Theater (1101 6th Street SW) this weekend and next. 8:00 p.m.</p>",
                "marker-symbol": "music"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.020945, 38.878241]
            }
        }, {
            "type": "Feature",
            "properties": {
                "description": "<div class=\"marker-title\">Truckeroo</div><p><a href=\"http://www.truckeroodc.com/www/\" target=\"_blank\">Truckeroo</a> brings dozens of food trucks, live music, and games to half and M Street SE (across from Navy Yard Metro Station) today from 11:00 a.m. to 11:00 p.m.</p>",
                "marker-symbol": "music"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-77.007481, 38.876516]
            }
        }]
    };