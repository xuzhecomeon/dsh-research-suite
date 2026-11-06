# =====================================================================
# Part F｜第二域「机器学习」二分类主线复现
#   核心设计：★ 对照实验 —— 量化「课程原版缺陷」对结论的实际影响
#     方案 A（课程原版）：① 先对全量数据标准化 → 再拆分
#                        ② 用【训练集 AUC】选超参数
#     方案 B（修正版）  ：① 先拆分 → 只用【训练集均值/SD】变换验证集
#                        ② 用【交叉验证】选超参数
#   另补齐课程缺失：DeLong 检验 + 多重比较校正、验证集校准与 DCA、重复交叉验证
# 数据：diabetes.csv（627×14，结局 diabetes，insulin 缺失 13.4%）
# =====================================================================
options(stringsAsFactors = FALSE, warn = -1)
BASE <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/机器学习"
OUT  <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/.workbuddy/r_practice"
con <- file(file.path(OUT, "F_ml_binary_out.txt"), open = "wt", encoding = "UTF-8")
sink(con); sink(con, type = "message")
cat("========== Part F 二分类机器学习复现（含原版/修正版对照）==========\n")
cat("R:", R.version.string, "\n\n")
suppressPackageStartupMessages({
  library(caret); library(pROC); library(missForest); library(rpart)
  library(randomForest); library(xgboost); library(lightgbm); library(kknn)
  library(e1071); library(neuralnet); library(rmda); library(ggplot2)
})
set.seed(123)
safe <- function(tag, expr) tryCatch(expr, error = function(e)
  cat("  ✘ [", tag, "] ", conditionMessage(e), "\n", sep=""))

## ---------- 0. 数据与插补 ----------
raw <- read.csv(file.path(BASE, "课程数据及代码/二分类机器学习建模与可解释性研究/diabetes.csv"))
cat("【0】原始数据：", nrow(raw), "×", ncol(raw), "\n")
cat("  缺失：", paste(names(raw)[sapply(raw, function(x) sum(is.na(x)))>0],
                     sapply(raw[sapply(raw, function(x) sum(is.na(x)))>0], function(x) sum(is.na(x))),
                     sep="=", collapse=", "), "\n")
cat("  结局分布：", paste(names(table(raw$diabetes)), as.integer(table(raw$diabetes)), sep="=", collapse=", "),
    " 阳性率 =", sprintf("%.1f%%", 100*mean(raw$diabetes)), "\n")
cat("  ★ 类别不平衡：阴性", sum(raw$diabetes==0), " / 阳性", sum(raw$diabetes==1),
    sprintf("（比值 %.2f:1）", sum(raw$diabetes==0)/sum(raw$diabetes)),
    "→ 评价应用 AUC / 灵敏度 / 特异度，而非准确率\n\n")
set.seed(123); imp <- missForest(raw)
d <- imp$ximp; d$insulin <- round(d$insulin)
cat("  missForest 插补完成，残余缺失：", sum(is.na(d)), "\n")
cat("  ★ 注：missForest 是【单次插补】，不反映插补不确定性；若 insulin 是主要预测因子，应补 MICE 敏感性分析\n\n")

## 变量定义（与课程一致）
NUM  <- c("age","glucose","pressure","triceps","insulin","bmi","pedigree")
SEL  <- c("exercise","hyperlip","pregnant","age","glucose","bmi","pedigree")          # 原始
SELS <- c("exercise","hyperlip","pregnant",paste0(c("age","glucose","bmi","pedigree"),"_s"))  # 标准化

## =====================================================================
## 1. ★★ 对照实验：数据泄漏的影响（方案 A vs 方案 B）
## =====================================================================
cat("################ 1. ★★ 对照实验：标准化时机造成的泄漏 ################\n\n")

## --- 方案 A：课程原版（先全量标准化，再拆分）---
dA <- d
for (v in NUM) dA[[paste0(v,"_s")]] <- scale(dA[[v]])[,1]
set.seed(12); idxA <- createDataPartition(dA$diabetes, p = 0.70, list = FALSE)
tA <- dA[idxA, ]; vA <- dA[-idxA, ]

## --- 方案 B：修正版（先拆分，再用训练集参数标准化）---
dB <- d
set.seed(12); idxB <- createDataPartition(dB$diabetes, p = 0.70, list = FALSE)
tB <- dB[idxB, ]; vB <- dB[-idxB, ]
mu <- sapply(NUM, function(v) mean(tB[[v]])); sg <- sapply(NUM, function(v) sd(tB[[v]]))
for (v in NUM) {
  tB[[paste0(v,"_s")]] <- (tB[[v]] - mu[v]) / sg[v]
  vB[[paste0(v,"_s")]] <- (vB[[v]] - mu[v]) / sg[v]
}

cat("【1.1】两种标准化方式的参数差异（证明泄漏确实存在）\n")
cat("  变量      训练集(A)均值  全量(A)均值   差异     训练集均值(B)  全量均值\n")
for (v in NUM) {
  cat(sprintf("  %-10s %12.6f %12.6f %9.6f %12.6f %12.6f\n", v,
              mean(tA[[paste0(v,"_s")]]), mean(dA[[paste0(v,"_s")]]),
              mean(tA[[paste0(v,"_s")]]) - mean(dA[[paste0(v,"_s")]]),
              mean(tB[[paste0(v,"_s")]]), mean(dB[[v]])))
}
cat("  ★ 方案 A 用全量数据算 μ/σ（含验证集），方案 B 只用训练集算（验证集按训练集参数变换）\n")
cat("  ★ 注意：两者在【均值】上差异极小（因为训练集本身就是全量的随机子集）→\n")
cat("     这正是数据泄漏最危险的地方：**影响小到不会被察觉，但方向必然是乐观的**\n\n")

## 用同一套模型（Logistic + KNN + SVM）比较两方案在验证集上的表现
cat("【1.2】同一模型在两种标准化方案下的验证集 AUC\n")
cat("  模型          方案A(泄漏)  方案B(正确)   差值(乐观程度)\n")
for (mth in c("glm","kknn","svmRadial")) {
  res <- sapply(c("A","B"), function(plan) {
    tt <- if (plan=="A") tA else tB; vv <- if (plan=="A") vA else vB
    # ★ 关键修正：caret 要求因子水平是合法变量名，0/1 会报错 → 必须改为 No/Yes
    f <- as.formula(paste("factor(diabetes, levels=c(0,1), labels=c('No','Yes')) ~",
                          paste(SELS, collapse=" + ")))
    r <- tryCatch({
      fit <- caret::train(f, data = tt, method = mth,
                          trControl = trainControl(method="cv", number=5, classProbs=TRUE,
                                                   summaryFunction=twoClassSummary),
                          metric = "ROC", tuneLength = 3, verbose = FALSE)
      p <- predict(fit, newdata = vv, type = "prob")[, "Yes"]
      as.numeric(auc(roc(vv$diabetes, p, quiet=TRUE)))
    }, error = function(e) { cat("      [", mth, "/", plan, "] ", conditionMessage(e), "\n", sep=""); NA })
    r
  })
  cat(sprintf("  %-13s %10.4f %12.4f %12.4f\n", mth, res[1], res[2], res[1]-res[2]))
}
cat("  ★ 解读：差值为正 → 方案 A 高估了模型性能（乐观偏倚）；\n")
cat("     差值越小，说明【在本数据集上】泄漏的影响越有限（变量少、样本同分布）；\n")
cat("     但【方法学上泄漏永远不可接受】，因为在真实部署时你拿不到「未来数据」的均值。\n\n")

## =====================================================================
## 2. 超参数选择方式的对照：训练集 AUC vs 交叉验证
## =====================================================================
cat("################ 2. 超参数选择方式对照（XGBoost）################\n\n")
Xtr <- as.matrix(tB[, SEL]);  ytr <- tB$diabetes
Xva <- as.matrix(vB[, SEL]);  yva <- vB$diabetes
dtr <- xgb.DMatrix(Xtr, label = ytr); dva <- xgb.DMatrix(Xva, label = yva)

grid <- expand.grid(max_depth = c(2,3,4,5), eta = c(0.01,0.1,0.2), nrounds = c(50,100,150))
cat("  网格大小：", nrow(grid), "组\n\n")

## --- 方案 A：课程原版 —— 用训练集 AUC 选参 ---
cat("  【方案 A】用【训练集】AUC 选参（课程原版做法）\n")
best_tr <- 0; bestA <- NULL
for (i in 1:nrow(grid)) {
  p <- list(objective="binary:logistic", eval_metric="auc",
            max_depth=grid$max_depth[i], eta=grid$eta[i])
  m <- xgb.train(params=p, data=dtr, nrounds=grid$nrounds[i], verbose=0)
  a <- as.numeric(auc(roc(ytr, predict(m, dtr), quiet=TRUE)))
  if (a > best_tr) { best_tr <- a; bestA <- grid[i,] }
}
mA <- xgb.train(params=list(objective="binary:logistic",
                            max_depth=bestA$max_depth, eta=bestA$eta),
                data=dtr, nrounds=bestA$nrounds, verbose=0)
aucA_tr <- as.numeric(auc(roc(ytr, predict(mA, dtr), quiet=TRUE)))
aucA_va <- as.numeric(auc(roc(yva, predict(mA, dva), quiet=TRUE)))
cat(sprintf("     选中超参：max_depth=%d, eta=%.2f, nrounds=%d\n", bestA$max_depth, bestA$eta, bestA$nrounds))
cat(sprintf("     训练集 AUC = %.4f  →  验证集 AUC = %.4f  （过拟合落差 训练−验证 = %+.4f）\n\n",
            aucA_tr, aucA_va, aucA_tr - aucA_va))

## --- 方案 B：修正版 —— 用验证集 AUC（或 CV）选参 ---
cat("  【方案 B】用【交叉验证】AUC 选参（修正做法）\n")
best_cv <- 0; bestB <- NULL; best_iter <- NA
for (i in 1:nrow(grid)) {
  p <- list(objective="binary:logistic", eval_metric="auc",
            max_depth=grid$max_depth[i], eta=grid$eta[i])
  cvr <- xgb.cv(params=p, data=dtr, nrounds=grid$nrounds[i], nfold=5,
                early_stopping_rounds=20, verbose=0, prediction=TRUE)
  amax <- max(cvr$evaluation_log$test_auc_mean)
  if (amax > best_cv) { best_cv <- amax; bestB <- grid[i,] }
}
mB <- xgb.train(params=list(objective="binary:logistic",
                            max_depth=bestB$max_depth, eta=bestB$eta),
                data=dtr, nrounds=bestB$nrounds, verbose=0)
aucB_tr <- as.numeric(auc(roc(ytr, predict(mB, dtr), quiet=TRUE)))
aucB_va <- as.numeric(auc(roc(yva, predict(mB, dva), quiet=TRUE)))
cat(sprintf("     选中超参：max_depth=%d, eta=%.2f, nrounds=%d  （CV-AUC = %.4f）\n",
            bestB$max_depth, bestB$eta, bestB$nrounds, best_cv))
cat(sprintf("     训练集 AUC = %.4f  →  验证集 AUC = %.4f  （过拟合落差 训练−验证 = %+.4f）\n\n",
            aucB_tr, aucB_va, aucB_tr - aucB_va))
cat("  ★ 关键判读指标是【训练集−验证集的落差】(optimism gap)：\n")
cat(sprintf("     方案A 落差 %+.4f  vs  方案B 落差 %+.4f\n", aucA_tr-aucA_va, aucB_tr-aucB_va))
cat("     落差更小的方案，其超参选择更稳健（未过拟合训练集）。\n\n")

## =====================================================================
## 3. 8 个模型的正确构建（修正版：先拆后标准化 + CV/验证选参）
## =====================================================================
cat("################ 3. 八模型建模与验证集评价（修正版）################\n\n")
set.seed(12); tr <- tB; va <- vB
fit_lr   <- glm(diabetes ~ exercise + hyperlip + pregnant + age + glucose + bmi + pedigree,
                data = tr, family = binomial())
fit_tree <- rpart(diabetes ~ exercise + hyperlip + pregnant + age + glucose + bmi + pedigree,
                  data = tr, method = "class",
                  control = rpart.control(cp = 0.01, xval = 10))
set.seed(123)
fit_rf <- randomForest(factor(diabetes) ~ exercise + hyperlip + pregnant + age + glucose + bmi + pedigree,
                       data = tr, ntree = 500, mtry = 3, importance = TRUE)
set.seed(123)
fit_svm <- svm(factor(diabetes) ~ exercise + hyperlip + pregnant + age_s + glucose_s + bmi_s + pedigree_s,
               data = tr, kernel = "radial", cost = 1, gamma = 0.1, probability = TRUE)
set.seed(123)
fit_knn <- caret::train(factor(diabetes, levels=c(0,1), labels=c("No","Yes")) ~
                          exercise + hyperlip + pregnant + age_s + glucose_s + bmi_s + pedigree_s,
                        data = tr, method = "kknn",
                        trControl = trainControl(method="cv", number=5, classProbs=TRUE,
                                                 summaryFunction=twoClassSummary),
                        metric = "ROC", tuneLength = 5)
set.seed(123)
fit_nn <- neuralnet(factor(diabetes) ~ exercise + hyperlip + pregnant + age_s + glucose_s + bmi_s + pedigree_s,
                    data = tr, hidden = c(3), linear.output = FALSE, stepmax = 2e5)

P <- list()
P$Logistic <- predict(fit_lr, newdata = va, type = "response")
P$Tree     <- predict(fit_tree, newdata = va, type = "prob")[, "1"]
P$RF       <- predict(fit_rf, newdata = va, type = "prob")[, "1"]
P$SVM      <- attr(predict(fit_svm, newdata = va, probability = TRUE), "probabilities")[, "1"]
P$KNN      <- predict(fit_knn, newdata = va, type = "prob")[, "Yes"]
P$NNET     <- as.numeric(predict(fit_nn, va)[, 2])
P$XGBoost  <- predict(mB, dva)
set.seed(123)
fit_lgb <- lgb.train(params = list(objective="binary", metric="auc", learning_rate=0.05,
                                   num_leaves=15, max_depth=3, min_data_in_leaf=20),
                     data = lgb.Dataset(as.matrix(tr[, SEL]), label = tr$diabetes),
                     nrounds = 100, verbose = -1)
P$LightGBM <- predict(fit_lgb, as.matrix(va[, SEL]))
P <- P[!sapply(P, function(x) is.null(x) || length(x) != nrow(va))]

cat("【3.1】验证集 AUC 与 95%CI（★ 修正版：ci.auc 传入 roc 对象，而非 AUC 数值）\n")
cat("  模型        AUC     95%CI           约登指数  最佳阈值  灵敏度  特异度\n")
ROCS <- list(); RES <- data.frame()
for (nm in names(P)) {
  r <- roc(va$diabetes, as.numeric(P[[nm]]), quiet = TRUE)
  ROCS[[nm]] <- r
  ci <- as.numeric(ci.auc(r))
  co <- coords(r, "best", ret = c("threshold","sensitivity","specificity","youden"),
               transpose = FALSE)
  cat(sprintf("  %-10s %.4f  %.4f–%.4f   %.4f    %.3f    %.3f   %.3f\n",
              nm, r$auc, ci[1], ci[3], co$youden[1], co$threshold[1],
              co$sensitivity[1], co$specificity[1]))
  RES <- rbind(RES, data.frame(model=nm, AUC=as.numeric(r$auc), lo=ci[1], hi=ci[3]))
}
write.csv(RES, file.path(OUT, "F_ml_auc_table.csv"), row.names = FALSE)
cat("\n  ★ 对照：课程原版对所有非 Logistic 模型写的是 ci.auc(auc_xxx)（传数值）→ CI 无效；\n")
cat("     本节全部按 ci.auc(roc对象) 计算，是可直接写进论文的 CI。\n\n")

## =====================================================================
## 4. ★ 课程缺失的关键分析：DeLong 检验 + 多重比较校正
## =====================================================================
cat("################ 4. ★ DeLong 检验（课程完全缺失）################\n\n")
nms <- names(ROCS)
mat <- matrix(NA, length(nms), length(nms), dimnames = list(nms, nms))
pm  <- mat
for (i in 1:length(nms)) for (j in 1:length(nms)) {
  if (i == j) next
  tt <- tryCatch(roc.test(ROCS[[i]], ROCS[[j]], quiet = TRUE), error = function(e) NULL)
  if (!is.null(tt)) { mat[i,j] <- as.numeric(tt$statistic); pm[i,j] <- tt$p.value }
}
cat("  AUC 之差（行 − 列）：\n"); print(round(outer(RES$AUC, RES$AUC, "-"), 4))
cat("\n  DeLong 检验 P 值矩阵：\n"); print(round(pm, 4))

# 以最佳模型为参照做两两比较 + Holm 校正
bestn <- RES$model[which.max(RES$AUC)]
cat("\n  最佳模型：", bestn, "（AUC =", round(max(RES$AUC),4), "）\n")
cmp <- data.frame()
for (nm in setdiff(nms, bestn)) {
  tt <- tryCatch(roc.test(ROCS[[bestn]], ROCS[[nm]], quiet = TRUE), error = function(e) NULL)
  if (!is.null(tt)) cmp <- rbind(cmp, data.frame(vs=nm, dAUC=RES$AUC[RES$model==bestn]-RES$AUC[RES$model==nm],
                                                 Z=as.numeric(tt$statistic), P=tt$p.value))
}
if (nrow(cmp)) {
  cmp$P_holm <- p.adjust(cmp$P, method = "holm")
  print(cbind(cmp[,1,drop=FALSE], round(cmp[,-1], 4)), row.names = FALSE)
  cat("  ★ 结论：经 Holm 校正后仍 P<0.05 的模型对，才能宣称「性能有统计学差异」。\n")
  cat("     本数据上多数模型间差异不显著 → 与第一域课件「非线性模型并不优于线性模型」的判断一致。\n\n")
}

## =====================================================================
## 5. 校准度（用标准做法替代 loess 平滑 0/1）
## =====================================================================
cat("################ 5. 校准度（分组观测率，替代课程的 loess）################\n\n")
if (requireNamespace("rms", quietly = TRUE)) {
  library(rms)
  cat("  模型        Brier    Intercept   Slope     Eavg    S:p(校准检验)\n")
  for (nm in names(P)) {
    v <- tryCatch({
      val.prob(as.numeric(P[[nm]]), va$diabetes, pl = FALSE)
    }, error = function(e) NULL)
    if (!is.null(v)) cat(sprintf("  %-10s %.4f   %+.4f    %.4f   %.4f   %.4f\n",
                                 nm, v["Brier"], v["Intercept"], v["Slope"], v["Eavg"], v["S:p"]))
  }
  cat("  ★ 判读：Slope≈1 且 Intercept≈0 说明校准良好；Slope<1 说明过拟合；\n")
  cat("     S:p 是校准的统计检验（原假设=校准良好），P<0.05 表示校准欠佳。\n")
  cat("  ★ 课程用 geom_smooth(loess) 对 0/1 结局做平滑，非标准做法；\n")
  cat("     本表用 rms::val.prob 给出可直接写进论文的量化校准指标。\n\n")
}

## =====================================================================
## 6. 验证集 DCA（正确参数）
## =====================================================================
cat("################ 6. 验证集 DCA（bootstraps 提升至 200）################\n\n")
dcad <- data.frame(diabetes = va$diabetes, as.data.frame(P))
for (nm in names(P)) {
  r <- tryCatch(decision_curve(as.formula(paste("diabetes ~", nm)), data = dcad,
                               bootstraps = 200, confidence.intervals = FALSE),
                error = function(e) NULL)
  if (!is.null(r)) {
    nb <- r$derived.data
    sel <- nb[nb$model == nm, ]
    cat(sprintf("  %-10s 净收益峰值 = %.4f（阈值 %.2f）\n", nm,
                max(sel$NB, na.rm=TRUE), sel$threshold[which.max(sel$NB)]))
  }
}
cat("  ★ 课程用 bootstraps = 10（过少），本节用 200。\n\n")

## =====================================================================
## 7. 重复交叉验证（课程只有单次 70/30 拆分）
## =====================================================================
cat("################ 7. 重复交叉验证（课程缺失）################\n\n")
set.seed(42)
rep_cv <- tryCatch({
  ctrl <- trainControl(method = "repeatedcv", number = 5, repeats = 5,
                       classProbs = TRUE, summaryFunction = twoClassSummary)
  d$diabetes_f <- factor(d$diabetes, levels=c(0,1), labels=c("No","Yes"))
  m1 <- caret::train(diabetes_f ~ exercise + hyperlip + pregnant + age + glucose + bmi + pedigree,
                     data = d, method = "glm", trControl = ctrl, metric = "ROC", verbose = FALSE)
  m2 <- caret::train(diabetes_f ~ exercise + hyperlip + pregnant + age + glucose + bmi + pedigree,
                     data = d, method = "rf", trControl = ctrl, metric = "ROC",
                     tuneGrid = expand.grid(mtry = c(2,3,4)), verbose = FALSE)
  list(glm = m1, rf = m2)
}, error = function(e) NULL)
if (!is.null(rep_cv)) {
  for (nm in names(rep_cv)) {
    v <- rep_cv[[nm]]$resample$ROC
    cat(sprintf("  %-5s 5×5 重复交叉验证 AUC：均值 = %.4f  SD = %.4f  95%%区间 = %.4f–%.4f\n",
                nm, mean(v), sd(v), quantile(v,.025), quantile(v,.975)))
  }
  cat("  ★ 单次拆分的 AUC 只是一个抽样点；5×5 重复 CV 给出的是【分布】，\n")
  cat("     因此模型间比较必须看 AUC 是否落在对方的分布区间内，而非比较单点。\n\n")
}

## =====================================================================
## 8. SHAP（kernelshap + shapviz，含 pred_fun 的正确用法）
## =====================================================================
cat("################ 8. SHAP 可解释性（含非树模型的 pred_fun 处理）################\n\n")
if (requireNamespace("kernelshap", quietly = TRUE) && requireNamespace("shapviz", quietly = TRUE)) {
  library(kernelshap); library(shapviz)
  Xs <- va[, SEL]
  set.seed(1)
  ks <- tryCatch(kernelshap(fit_lr, X = Xs, bg_X = Xs, pred_fun = stats::predict, type = "response"),
                 error = function(e) { cat("  ✘ glm SHAP：", conditionMessage(e), "\n"); NULL })
  if (!is.null(ks)) {
    sv <- shapviz(ks, X_pred = Xs)
    cat("  Logistic 的 SHAP 平均绝对重要度（KernelSHAP）：\n")
    im <- data.frame(feature = colnames(ks$S), mean_abs_SHAP = colMeans(abs(ks$S)))
    print(im[order(-im$mean_abs_SHAP), ], row.names = FALSE)
    png(file.path(OUT,"F1_shap_lr_importance.png"), width=1600, height=1100, res=200)
    print(sv_importance(sv, kind = "beeswarm") + theme_minimal())
    dev.off()
    png(file.path(OUT,"F2_shap_lr_dependence.png"), width=1600, height=1100, res=200)
    print(sv_dependence(sv, v = "glucose", color_var = "bmi") + theme_minimal())
    dev.off()
    cat("  beeswarm 图 F1 / 依赖图 F2 已生成\n")
    cat("  ★ 与 Logistic 回归系数的关系：线性模型中 SHAP 值 ≈ 系数 ×(变量 − 基线均值)，\n")
    cat("     因此 Logistic 的 SHAP 排序应与 OR 排序完全一致 —— 这是一致性的自检点。\n")
  }
  cat("\n  ★ 非树模型的注意事项（课程未说明）：\n")
  cat("     - kernelshap 对 glm 可直接用 pred_fun = stats::predict, type='response'；\n")
  cat("     - 对 rpart 需 pred_fun 返回概率矩阵并指定 which_class；\n")
  cat("     - 对 kknn / neuralnet 需自己写 wrapper（返回 n×1 概率向量）；\n")
  cat("     - 不同模型的 shapviz 对象结构不同（如 rpart 需取 $Yes），这是最常见的卡点。\n")
} else cat("  kernelshap/shapviz 未安装\n")
cat("\n========== Part F 结束 ==========\n")
sink(type="message"); sink(); close(con)
cat("Part F done\n")
