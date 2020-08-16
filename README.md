# YouTube Transcript Dataset Creator

The goal of this project is to create a UI that facilitates the creation of NLP datasets from YouTube transcripts.
Instead of manually searching and curating videos, we enter the search term and then determine which videos to add using the UI.
Then we finalize the selection and the transcripts are automatically downloaded and saved in a convenient pandas pkl format.
This allows for a modular dataset design so that we can easily add or remove results at a later date.

<img src="https://github.com/JohnRResearch/YouTubeDatasetCreator/blob/master/documentation/Search.png">

This greatly speeds up the creation of datasets for NLP applications such as authorship identification, sentiment analysis, or predictive text generation.

For further details, please see [YouTubeDatasetCreator.ipynb](https://github.com/JohnRResearch/YouTubeDatasetCreator/blob/master/YouTubeDatasetCreator.ipynb) which walks through creating a dataset with this tool.
