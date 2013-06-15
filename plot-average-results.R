# plot-results.R
#
# run with:
# $ R CMD BATCH plot-results.R

## uncomment to output as .eps file
postscript(file="incident-distances.eps",
           paper="special",
           width=10,
           height=10,
           horizontal=FALSE)

#png("distances.png")

# read data from csv
mydata <- read.csv('results.csv')

# plot distances
mp <- barplot(mydata$distance, main='distance from scenario incident', ylim=c(0,600), xlab='angles (degrees)', ylab='distance (m)',las=2)

# show distances on bars
text(mp, 1:7, labels = mydata$distance, pos = 3)

# generate x axis data and show on graph
angles <- paste(c("0"), mydata$angle, sep="-")
axis(side=1, at=mp, labels=NA)
text(mp, mp-30, srt=45, labels=angles, xpd=TRUE)

# draw scenario result lines with distances
#abline(h = 379, col = "red")
abline(h = 408, col = "red")
#text(2.4, 360, "distance using 19 reports (379m)")
text(1.4, 400, "distance using 12 reports (408m)")

# NOTE: this is included as the last plot bar 0-360 degrees
#abline(h = 295, col = "blue")
#text(2.9, 265, "distance using average calculated incidents (295m)")

dev.off()
