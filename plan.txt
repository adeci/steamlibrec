STEAMLIBREC

Part 1 GATHER:
	Get users library data and playtimes
	Keep their top 10 games by playtime
	Create list of all the games across all libraries
	Get the top 5 most popular tags for every game
	Export two dictionaries in json format:
		Dict1: Libraries that have game key and playtime value
		Dict2: game key and tags (list) for every game across all libs
Part 2 PARSE:
	Tag Prep:
		Collect a list of all the tags across all the libraries
		Rank them on frequency
		Eliminate tags that appear very rarely, determine keep %
		Iterate through Dict2 and elimiate tags that are irrelevant
		Keep only 3 tags per game max
		Create a list of all unique tags across all the games
	User Prep:
		Distribute playtime for each game split between the tags for that game
		Aggregate playtimes for tags for each user (Sum like tags)
		Create a User-Tag playtime matrix for each user:
			Each row is a user, each columns is a unique tag (fill w aggregate tag playtimes)
			For tags with no playtime fill with 0.
		Normalize the matrices with Row-wise normalization
			Row-wise chosen to keep relative interest based on playtime for each unique lib
	Export in json format:
		Modified game-tag dict with only top3 for use for single lib prediction later
		Training data 
Part 3:
	Inspect dataframe
	Train clustering model
	Create recommender and use model to rec based on single lib input
