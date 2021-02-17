# Dice crawler
This is an experimental script created for solving some tasks of probability theory. It allows to combine discrete finite random events into mathematical expressions and get probability of each outcome of that expression. 

Example of usage (probabilities of 2d6 roll):
>>> import dice_crawler
>>> 
>>> dice_crawler.roll_d6() + dice_crawler.roll_d6() > 7

Output:
>>> False    0.583333
>>> 
>>> True     0.416667
>>> 
>>> dtype: float64
