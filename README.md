# winebot
a content and collaborative filtering bot for recommendations and pairings in an easy conversational style

# parameters
### gauth:
provide your google api id from https://console.cloud.google.com. This is needed for sending requests through the api

### hospitals
a dictionary that stores a list of addresses which we use as the origin point for the isochrome. It can be replaced by anything else

### drivetime: default 10]
how far should the boundary be set from your origin point. Mode of transportis controlled separately, so the boundary will change for differnet modes

### num_angs: [default 62]
the number of points to map around the origin. Fewer points means the algorithm runs faster, but also creates more jagged features

### tolerance [default .9]
the number of minutes that a test point can be away from duration to be considered acceptable

### maxits [default 10]
the number of iterations to try to get to an acceptable solution.

### alpha
a learning rate that changes the size of each step in the algorithm. The closer the current distance, the smaller the step

# dependencies
### Python packages
-geocoder -requests -time -pandas -math -simplejson, urllib.request -googlemaps -datetime
