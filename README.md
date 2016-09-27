# Beer Learning

This will be a repo for me to play with downloading recipes and performing some machine learning on them as it regards to my favorite hobby--Beer!!

Did most of my work in downloading, parsing, cleaning BeerXML data from
BrewToad.

Using fermentables and hops as my features, I examined a few algorithms
to classify recipes to styles which can be found in src/styleClassification.ipynb:
* Logistic Regression
* Naive Bayes
* SVM
* Decision Trees

With ~115M of data (or about 500 pages of BrewToad recipes out of over
10,000) Decision Trees came out the clear winner classifying recipes
correctly about 45% of the time. LogReg and SVM were around 30% and
Naive Bayes was terrible at 10%. NB actually got worse with more data.

I also plan to play with RNNs to generate sequences of recipes per style. We'll see what happens...
