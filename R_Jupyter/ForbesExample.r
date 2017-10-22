
M <- matrix(1:16, 4,4)
M

apply(M, 1, min) # apply function 'min' to rows
apply(M, 2, max) # apply function 'max' to columns

# lapply and sapply example
x <- list(a=1, b=1:3, c=10:100) # x is a jagged array with three variables of unequal length

lapply(x, length) # apply the function to length for each column of x

sapply(x, length) # sapply is a wrapper to lapply. they are compliments

lapply(x, sum)

sapply(x, sum)

sapply(1:5, function(x)rnorm(3, mean=x)) # each column has a mean of 1:5

# read data from online source
forbes <- read.csv("http://statweb.lsu.edu/faculty/li/data/Forbes2000.csv", header=T)

head(forbes)  #display the first few rows of data with. 
              # end of the data can be displayed with tail function

class(forbes)  # check if the data read is in a data frame

str(forbes)  # str displays structure of the R object

print("Dimensions of Forbes data")
print(dim(forbes))  # what are dimensions of the object
print("Number of Rows")
print(nrow(forbes)) # print number of rows/observations
print("Number of Columns")
print(ncol(forbes)) # print number of columns (variables) of data
print("Variable Names")
print(names(forbes)) # print out names of the columns

class(forbes[,"category"])  # what is the datatype of 'category'
nlevels(forbes[,"category"]) # how many levels does category have
levels(forbes[,'category']) # list names of categories

table(forbes[,'category']) # frequency table for categories

print('Data type of variable Sales')
class(forbes[,5]) # data type of varible sales
print('Standard statistics and summary for Sales')
median(forbes[,5]) # calculate median for sales
mean(forbes[,5]) # calculate mean for sales
sd(forbes[,5]) # calculate sd for sales
range(forbes[,5]) # calculate range for sales
summary(forbes[,5]) # summarize data for sales

# all these statements do the same thing
companies <- forbes$name
companies <- forbes[,"name"]
companies <- forbes[,2] 

order_sales <- order(forbes$sales) # default ordering is ascending by sales
companies[order_sales[1:3]] # print out the first three companies with least sales

orderSales2 <- order(forbes$sales, decreasing=T) # order in decreasingly by sales
companies[orderSales2[1:3]]  # first three companies with highest sales
forbes[orderSales2[1:3],] # get information about these three companies from orig. data

# list companies with assets of more than 100 billion, only selected variables
forbes[forbes$assets>1000,c('name','sales','profits','assets')]

# list companies with missing values of profits
na_profits <- is.na(forbes$profits) # a logic vector of length = nrows(forbes$profits)
class(na_profits)

table(na_profits)

#forbes[na_profits,c(1:2,5:7)]# == forbes[na_profits, c('rank','name','sales','profits','assets')]
forbes[na_profits, c('rank','name','sales','profits','assets')]

# subset of forbes dataset, list of all companies in United Kingdom
ukCompanies <- forbes[forbes$country == 'United Kingdom',]
nrow(ukCompanies)
ukCompanies <- subset(forbes, country == 'United Kingdom')
nrow(ukCompanies)

# negative index removes absolute value of that positioned data
# summary statistics of the dataset
summary(forbes[,-2])
# lapply(forbes[,-2], summary)

# categorizes numeric data (profits) by category. The first paramater has to be numeric
mprofits1 <- tapply(forbes$profits, forbes$category, median)
mprofits1

# the same function as above but with NA removed
mprofits2 <- tapply(forbes$profits, forbes$category, median, na.rm=T)
mprofits2

# sort from highest to lowest and print the first three.
sort(mprofits2, decreasing=T)[1:3]

# print quantiles of profit ratios
quantile(forbes$profits, prob=c(0,0,0.25,0.5,0.75,1), na.rm=T)

# calculate the IQR for profits
print('IQR:')
IQR(forbes$profits, na.rm=T)

# Categories with the min and max IQR
iqrProfits <- tapply(forbes$profits, forbes$category, IQR, na.rm=T)
levels(forbes$category)[which.min(iqrProfits)]
levels(forbes$category)[which.max(iqrProfits)]
#less variable profits in tourism enterprises compared with 
#profits in the pharmaceutical industr

# create boxplots on sales volumw with jpef format
jpeg(filename="forbes.jpg", width=1200, height=800, quality=75, bg='white')
par(mar=c(12,4,2,2)) # Set margins: bottom top, left, right
boxplot(sales~category, data=forbes, names=NULL, xaxt='n', col='yellow')
labels <- levels(forbes$category)
text(1:27, rep(-20,27), srt=45, adj=1, labels=labels, xpd=T)
dev.off()

# What does this do ?????
tmp <- subset(forbes, country %in% c('United Kingdom','Germany','India','Turkey'))
dim(tmp)
# Below is i think essentially useless code.
# it assigns to countries the column of countries.
tmp$country <- tmp$country[,drop=T] # drop rest of the countries
nlevels(tmp$country)

# output .tiff format
tiff(filename='forbes.tiff', width=800, height=600, bg='white')
par(mar=c(5,5,2,2), cex.lab=2, cex.axis=1.5)
plot(log(marketvalue)~country, data=tmp, ylab='log(marketvalue)', varwidth=T)
dev.off()

# Histogram of market values with .bmp format
bmp(filename='forbes.bmp', width=800, height=1200, bg='white')
par(mar=c(5,5,4,2), cex.lab=2, cex.axis=1.5, cex.main=2.5)
layout(matrix(1:3, nrow=3))
hist(forbes$marketvalue, breaks=50,
    freq=F, main="Density Plot of market value")
hist(log(forbes$marketvalue), breaks=50, # natural log
    freq=F, main="Density Plot of Log(marketvalue)")
hist(log10(forbes$marketvalue), breaks=50, #log base 10
    freq=F, main="Density plot of log10(market value)")
lines(density(log10(forbes$marketvalue)), lty=1, lwd=2,col='blue')
dev.off()

# Scatter plot of marketvalue vs. sales
par(mfrow=c(2,1), mar=c(4,4,2,2))
plot(log(marketvalue)~log(sales),data=forbes)
plot(log(marketvalue)~log(sales), data=forbes, pch='.')
# Add a regression line
abline(lm(log(marketvalue)~log(sales), data=forbes), col='red', lty=3, lwd=2)
# Add another lowess smoother (nonlinear)
lines(lowess(log(forbes$sales), log(forbes$marketvalue)), col='blue', lty=3, lwd=2)
#legend(locator(l), legend=c("Linear","Lowess"), lty=c(2,3), lwd=c(2,2), col=c('red','blue'))

library(hexbin)

plot(hexbin(log(forbes$marketvalue), log(forbes$sales), xbins=50,
            xbnds=range(log(forbes$marketvalue)), ybnds=range(log(forbes$sales))))

library(car)

scatterplot(log(sales)~log(marketvalue),data=forbes,
           xlab='log(marketvalue)', ylab='log(sales)',main="Enhanced Scatter Plot")

# Scatter plot matrix
library(lattice)
tmp <- subset(forbes, country %in% c('China','India','Singapore'))
tmp[,5:8] <- log(tmp[,5:8])
tmp$country <- tmp$country[,drop=T]
table(tmp$country)

pairs(~sales+profits+assets+marketvalue, data=tmp,
      main="Scatterplot Matrix", panel=panel.smooth)

super.sym <- trellis.par.get("superpose.symbol")
splom(~tmp[,5:8],
      groups=tmp$country,
      panel=panel.superpose,
      key=list(title="Three countries",
      columns=3,
      points=list(pch=super.sym$pch[1:3],
      col=super.sym$col[1:3]0),
      lwd=2,
      cex=1.5,
      text=list(c("China", "India", "singapore"))))
# parallel plot
parallelplot(~tmp[,5:8], horizontal.axis=F)

#Create another data frame with only numeric variables
forbes2 <- data.frame(sales=forbes$sale,profits=forbes$profits,
           assets=forbes$assets, mvalue=forbes$marketvalue)

fit1 <- lm(mvalue ~ ., data=forbes2[1:1500,])

summary(fit1)

length(fit1$fit)

length(fit1$residual)

which(is.na(forbes2$profits[1:1500]))

plot(forbes2$mvalue[which(!is.na(forbes$profits[1:1500]))],
    fit1$fit, pch='o', xlab='Market value', ylab='Fitted Value')
lines(c(0,250), c(0,250))

cor(forbes2$mvalue[which(!is.na(forbes2$profits[1:1500]))],
     fit1$fit,use="complete.obs")

ndata= forbes2[1501:2000,]
pred1 <- predict(fit1, newdata=ndata)
plot(ndata$mvalue, pred1, pch='o', xlab="Market Value", ylab="Predicted Value")

cor(ndata$mvalue,pred1, use='complete.obs')

par(mfrow=c(2,2))
plot(1:2000, forbes2$sales, cex=2, pch='.')
plot(1:2000, forbes2$profits, cex=2, pch='.')
plot(1:2000, forbes2$assets, cex=2, pch='.')
plot(1:2000, forbes2$mvalue, cex=2, pch='.')

forbes2 <- forbes2[which(!is.na(forbes2$profits)),]
dim(forbes2)

set.seed(1)
idx <- sample(1:1995, size=1995, replace=F)
fit2 <- lm(mvalue ~ ., data=forbes2[idx[1:1500],])
summary(fit2)

plot(forbes2$mvalue[idx[1:1500]], fit2$fit, pch='o', xlab='Market Value', ylab='Fitted Value')
lines(c(0,200), c(0,200))

pred2 <- predict(fit2, newdata=forbes2[idx[1501:1995],])

plot(forbes2$mvalue[idx[1501:1995]],pred2,pch='o',xlab="Market value",ylab="Predicted value")

cor(forbes2$mvalue[idx[1501:1995]],pred2)

1-sum((forbes2$mvalue[idx[1501:1995]]-pred2)^2)/
sum((forbes2$mvalue[idx[1501:1995]]-mean(forbes2$mvalue[idx[1501:1995]]))^2)


