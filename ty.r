 
# ROC curve example using R language
library(pROC)
data(aSAH)
roc_obj <- roc(aSAH$outcome, aSAH$s100b)
plot(roc_obj, print.thres = "best", main = "ROC Curve Example")

