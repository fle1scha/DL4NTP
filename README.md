# DL4NTP
## Ant To-Do:
1. Combine Date and first-seen. DONE
- Find way to get new Datetime variable into milliseconds or ordinal encoding. DONE
2. Define binary holiday variable. DONE but can't compare Date column with date range for some reason.
3. Fix preprocessing for SANREN[300something] DONE
4. Set limit on one-hot encoding unqiue values based off literature. DONE - removed IPAddress categories
5. Determine how to get LSTM to predict other variables. 
6. Hyperparameter optimisation via literature.

## Research Questions to Answer
1. How does the SANReN traffic data vary with time
and day in relation to the South African university
calendar?
2. Which of the LSTM architectures, baseline, bilateral
or stacked, provides the highest prediction accuracy,
subject to network constraints?
3. What is the computational cost of different LSTM?

## Theory
1. Deep Learning Basics https://colab.research.google.com/github/lexfridman/mit-deep-learning/blob/master/tutorial_deep_learning_basics/deep_learning_basics.ipynb
2. Adam Optimization https://www.coursera.org/lecture/deep-neural-network/adam-optimization-algorithm-w9VCZ?utm_campaign=The%20Batch&utm_medium=email&_hsmi=148614359&utm_content=148611472&utm_source=hs_email
3. Illustrated Guide to LSTMs https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21
4. Understanding LSTMS https://colah.github.io/posts/2015-08-Understanding-LSTMs/

## Josiah suggestions
1. Field for internal or external IP addresses. Geolococation method. 
2. Will doubling the number of data points double the training time? Grid search over data points and training times and report.
3. Dataset size vs accuracy 
4. Training time vs accuracy
5. In a given time period, how many flows are there? Total bytes per period might also be useful. 