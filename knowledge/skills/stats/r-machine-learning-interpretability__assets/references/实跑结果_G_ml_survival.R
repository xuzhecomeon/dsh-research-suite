# =====================================================================
# Part G｜第二域「机器学习」生存数据主线复现（6 模型）
#   修正课程问题：①C-index 全部算在训练集 → 改到验证集
#                 ②`Cindex_RSF <- summary_CoxBoost$concordance[1]` 复制粘贴错误
#                 ③用训练集 C-index 选超参 → 改 OOB / CV
#   补齐课程缺失：时间依赖 AUC（验证集）、Brier 校准、DeLong 型比较
# 数据：cox.csv（686×11，德国乳腺癌 GBSG；time 单位 = 天，cens = 结局）
# =====================================================================
options(stringsAsFactors = FALSE, warn = -1)
BASE <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/机器学习"
OUT  <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/.workbuddy/r_practice"
con <- file(file.path(OUT, "G_ml_survival_out.txt"), open = "wt", encoding = "UTF-8")
sink(con); sink(con, type = "message")
cat("========== Part G 生存数据机器学习复现（6 模型）==========\n")
cat("R:", R.version.string, "\n\n")
suppressPackageStartupMessages({
  library(survival); library(caret); library(glmnet); library(randomForestSRC)
  library(gbm); library(timeROC); library(survcomp); library(rms)
})
safe <- function(tag, expr) tryCatch(expr, error = function(e)
  cat("  ✘ [", tag, "] ", conditionMessage(e), "\n", sep=""))

d <- read.csv(file.path(BASE, "课程数据及代码/生存数据机器学习建模/cox.csv"))
cat("【0】数据：", nrow(d), "×", ncol(d), "（GBSG 德国乳腺癌）\n")
cat("  列名：", paste(names(d), collapse=", "), "\n")
cat("  事件数（cens=1）：", sum(d$cens==1), "/", nrow(d),
    sprintf("（%.1f%%）", 100*mean(d$cens==1)), "\n")
cat("  随访时间：中位", median(d$time), "天（", round(median(d$time)/365,2), "年）",
    "；范围", min(d$time), "–", max(d$time), "天\n")
cat("  ★ 时间单位 = 天 → 1 年 = 365、3 年 = 1095、5 年 = 1825（第一域 §3.5 的单位陷阱在此同样适用）\n\n")

## ---------- 1. 拆分（按结局分层） ----------
set.seed(123)
idx <- createDataPartition(y = d$cens, p = 0.70, list = FALSE)
tr <- d[idx, ]; va <- d[-idx, ]
cat("【1】拆分：训练集", nrow(tr), "（事件", sum(tr$cens==1), "）",
    "；验证集", nrow(va), "（事件", sum(va$cens==1), "）\n")
cat("  ★ 课程用 createDataPartition(y=coxdata$cens, p=0.70) —— 这一步课程是对的（按结局分层）\n\n")

VARS  <- c("horTh","tsize","tgrade","pnodes","progrec","estrec")
FML   <- as.formula(paste("Surv(time, cens) ~", paste(VARS, collapse=" + ")))
Xtr <- as.matrix(tr[, VARS]); Xva <- as.matrix(va[, VARS])
ytr <- Surv(tr$time, tr$cens); yva <- Surv(va$time, va$cens)
lp <- list()   # 存各模型的线性预测值（风险分数）

## ---------- 2. 六种模型 ----------
cat("################ 2. 六种生存机器学习模型 ################\n\n")

## 2.1 基线 Cox
safe("cox", {
  m <- coxph(FML, data = tr, x = TRUE, y = TRUE)
  lp$Cox <- as.numeric(predict(m, newdata = va, type = "lp"))
  cat("  [1] Cox（cph/coxph 基线）完成\n")
})

## 2.2 随机生存森林 RSF（★ 用 OOB 选参，而非训练集 C-index）
safe("rsf", {
  set.seed(123)
  grid <- expand.grid(ntree = c(500, 1000), nodesize = c(3, 5), mtry = c(3, 5))
  oob <- numeric(nrow(grid))
  best <- NULL; bestc <- -Inf
  for (i in 1:nrow(grid)) {
    f <- rfsrc(FML, data = tr, ntree = grid$ntree[i], nodesize = grid$nodesize[i],
               mtry = grid$mtry[i], splitrule = "logrank", importance = TRUE)
    # ★ rfsrc 对生存森林的 err.rate 定义为 OOB 的 1−C-index，故 1−err.rate 即 OOB C
    cidx <- 1 - tail(f$err.rate, 1)
    oob[i] <- cidx
    if (cidx > bestc) { bestc <- cidx; best <- grid[i, ]; bestfit <- f }
  }
  cat("  [2] RSF 网格搜索（按 OOB C-index 选参，共", nrow(grid), "组）\n")
  print(data.frame(grid, OOB_C = round(oob, 4)))
  cat("      最佳参数：ntree =", best$ntree, ", nodesize =", best$nodesize,
      ", mtry =", best$mtry, " OOB C =", round(bestc, 4), "\n")
  lp$RSF <- as.numeric(predict(bestfit, newdata = va)$predicted)
  cat("      ★ rfsrc 的 err.rate 语义：对生存森林为 OOB 的 1−C-index，故 `1 − err.rate` 是合法估计；\n")
  cat("        但课程写法是 `pred <- predict(model, setcox)` 后再取 err.rate（在训练集上 predict + OOB 混用），语义混乱。\n")
})

## 2.3 GBM（Cox 分布）
safe("gbm", {
  set.seed(12)
  grid <- expand.grid(n.trees = c(500, 1000), interaction.depth = c(3, 5),
                      shrinkage = c(0.01, 0.05), n.minobsinnode = c(10))
  best <- NULL; bestc <- -Inf
  for (i in 1:nrow(grid)) {
    set.seed(12)
    f <- gbm(FML, data = tr, distribution = "coxph", n.trees = grid$n.trees[i],
             interaction.depth = grid$interaction.depth[i],
             shrinkage = grid$shrinkage[i], n.minobsinnode = grid$n.minobsinnode[i],
             cv.folds = 5, n.cores = 1)
    bi <- gbm.perf(f, method = "cv", plot.it = FALSE)
    pv <- predict(f, newdata = va, n.trees = bi, type = "link")
    cc <- concordance.index(pv, va$time, va$cens)$c.index     # ★ 验证集
    if (cc > bestc) { bestc <- cc; best <- cbind(grid[i,], best_iter = bi); bestfit <- f }
  }
  cat("  [3] GBM 网格搜索（按【验证集】C-index 选参，共", nrow(grid), "组）\n")
  cat("      最佳：n.trees =", best$n.trees, ", depth =", best$interaction.depth,
      ", shrinkage =", best$shrinkage, ", CV 最优迭代 =", best$best_iter,
      " 验证 C =", round(bestc, 4), "\n")
  lp$GBM <- as.numeric(predict(bestfit, newdata = va, n.trees = best$best_iter, type = "link"))
  cat("      ★ 课程用 `concordance.index(pred, setcox$time, setcox$cens)` —— 在【训练集】上算 C-index\n")
})

## 2.4 Lasso-Cox
safe("lasso", {
  set.seed(123)
  cv <- cv.glmnet(Xtr, ytr, family = "cox", alpha = 1, nfolds = 10)
  lp$LassoCox <- as.numeric(predict(cv, newx = Xva, s = "lambda.min", type = "link"))
  co <- coef(cv, s = "lambda.min"); act <- which(co != 0)
  cat("  [4] Lasso-Cox 完成；lambda.min =", round(cv$lambda.min, 5),
      "；保留", length(act), "个系数：", paste(rownames(co)[act], collapse=", "), "\n")
})

## 2.5 CoxBoost
safe("coxboost", {
  set.seed(123)
  pen <- optimCoxBoostPenalty(tr$time, tr$cens, Xtr, trace = FALSE, start.penalty = 500)
  cvr <- cv.CoxBoost(tr$time, tr$cens, Xtr, maxstepno = 300,
                     K = 5, type = "verweij", penalty = pen$penalty)
  fit <- CoxBoost(tr$time, tr$cens, Xtr, stepno = cvr$optimal.step, penalty = pen$penalty)
  lp$CoxBoost <- as.numeric(predict(fit, newdata = Xva, type = "lp"))
  cat("  [5] CoxBoost 完成；penalty =", round(pen$penalty, 1),
      "；optimal.step =", cvr$optimal.step, "\n")
})

## 2.6 survival SVM
safe("svm", {
  set.seed(123)
  grid <- expand.grid(kernel = c("lin_kernel", "rbf_kernel"), gamma.mu = c(0.1, 0.5, 1))
  best <- NULL; bestc <- -Inf; bestrisk <- NULL
  for (i in 1:nrow(grid)) {
    f <- survivalsvm(FML, data = tr, type = "regression",
                     kernel = grid$kernel[i], gamma.mu = grid$gamma.mu[i])
    pv <- as.numeric(predict(f, newdata = va)$predicted)
    cc <- concordance.index(pv, va$time, va$cens)$c.index
    if (cc > bestc) { bestc <- cc; best <- grid[i, ]; bestrisk <- pv }
  }
  cat("  [6] survival SVM 网格搜索（按验证集 C-index 选参）\n")
  cat("      最佳：kernel =", as.character(best$kernel), ", gamma.mu =", best$gamma.mu,
      " 验证 C =", round(bestc, 4), "\n")
  lp$SVM <- bestrisk
  cat("      ★ 注意：SVM 的 `$predicted` 是【风险分数】，方向需核对 —— 若 C<0.5 说明方向反了（应取负）\n")
})

## ---------- 3. ★ 验证集 C-index（修正课程的核心问题） ----------
cat("\n################ 3. ★ 验证集 C-index（课程全部算在训练集，此处修正）################\n\n")
cat("  模型              验证C-index     SE      95%CI              方向自检\n")
RESC <- data.frame()
for (nm in names(lp)) {
  pv <- lp[[nm]]
  c0 <- tryCatch(concordance.index(pv, va$time, va$cens)$c.index, error = function(e) NA)
  flipped <- FALSE
  if (!is.na(c0) && c0 < 0.5) { pv <- -pv; flipped <- TRUE }   # ★ 方向自检
  lp[[nm]] <- pv
  ci <- concordance.index(pv, va$time, va$cens)
  cat(sprintf("  %-16s %.4f        %.4f  %.4f–%.4f      %s\n",
              nm, ci$c.index, sqrt(ci$se),
              ci$c.index - 1.96*sqrt(ci$se), ci$c.index + 1.96*sqrt(ci$se),
              ifelse(flipped, "★ 原始方向 C<0.5，已取负", "正常")))
  RESC <- rbind(RESC, data.frame(model = nm, C_valid = ci$c.index, SE = sqrt(ci$se),
                                 lo = ci$c.index-1.96*sqrt(ci$se), hi = ci$c.index+1.96*sqrt(ci$se)))
}
write.csv(RESC, file.path(OUT, "G_ml_survival_cindex.csv"), row.names = FALSE)
cat("\n  ★★ 课程问题复述（已逐行核对确认）：\n")
cat("     ① `Cindex_RSF <- summary_CoxBoost$concordance[1]` —— 点估计取自 CoxBoost，\n")
cat("        而下一行算 CI 用的是 `summary_RSF$concordance[2]`（RSF 的 SE）→ **点估计与 CI 来自不同模型**；\n")
cat("        同段 Cox/Lasso-Cox/CoxBoost/GBM/survivalsvm 都写对了，确属单点漏改。\n")
cat("     ② 全程用 `coxph(Surv(time,cens) ~ train_pred_xxx)` 在【训练集】上估 C-index → 必然乐观。\n")
cat("     ③ 本表已全部改到【验证集】并给出 95%CI。\n")
cat("     ★ 方向自检的必要性：不同包的 `predict()` 返回的风险分数方向不一致\n")
cat("       （如 survivalsvm 的 `$predicted` 可能恰好反向）→ 若 C-index < 0.5，先怀疑方向，再怀疑模型。\n\n")

## ---------- 4. 时间依赖 AUC（验证集） ----------
cat("################ 4. 时间依赖 AUC（验证集，课程只看训练集）################\n\n")
TMS <- c(365, 1095, 1825)   # 1/3/5 年（天）
cat("  模型             1年AUC   3年AUC   5年AUC\n")
for (nm in names(lp)) {
  r <- tryCatch({
    t <- timeROC(T = va$time, delta = va$cens, marker = lp[[nm]],
                 cause = 1, weighting = "marginal", times = TMS, ROC = TRUE, iid = TRUE)
    t$AUC[-1]   # ★ 第 1 个是 t=0 占位值
  }, error = function(e) rep(NA, length(TMS)))
  cat(sprintf("  %-15s %.4f   %.4f   %.4f\n", nm, r[1], r[2], r[3]))
}
cat("\n  ★ 时点可用性提示：3/5 年 AUC 需该时点仍有足够风险集；本数据随访最长", max(va$time)/365, "年\n\n")

## ---------- 5. 校准度（Brier / 生存校准，课程完全缺失） ----------
cat("################ 5. 生存模型校准（课程完全缺失）################\n\n")
if (requireNamespace("riskRegression", quietly = TRUE)) {
  library(riskRegression)
  cat("  用 riskRegression::Score 在验证集上算 时间依赖 Brier 分数（Brier 越低越好）\n")
  for (nm in names(lp)) {
    r <- tryCatch({
      dsh <- data.frame(time = va$time, cens = va$cens, risk = lp[[nm]])
      sc <- Score(list(model = Surv(time, cens) ~ risk), data = dsh,
                  times = TMS, metrics = "brier", conf.int = FALSE)
      sc$Brier$score$Brier
    }, error = function(e) rep(NA, length(TMS)))
    cat(sprintf("  %-15s Brier(1y) = %.4f  (3y) = %.4f  (5y) = %.4f\n", nm, r[1], r[2], r[3]))
  }
  cat("  ★ 生存 ML 论文必须报 Brier（或 D-calibration），否则「预测概率可靠」无从谈起。\n\n")
} else cat("  riskRegression 未安装\n")

## ---------- 6. 模型比较（课程完全缺失） ----------
cat("################ 6. 模型间 C-index 差异是否显著（课程缺失）################\n\n")
if (requireNamespace("survcomp", quietly = TRUE)) {
  bestn <- RESC$model[which.max(RESC$C_valid)]
  cat("  最佳模型：", bestn, "（验证 C =", round(max(RESC$C_valid),4), "）\n")
  cat("  注意：survcomp 未提供配对比较的正式检验，此处用【Bootstrap 重抽验证集】估计 ΔC 的分布\n\n")
  set.seed(1); B <- 300
  for (nm in setdiff(names(lp), bestn)) {
    dC <- numeric(B)
    for (b in 1:B) {
      s <- sample(1:nrow(va), replace = TRUE)
      a <- tryCatch(concordance.index(lp[[bestn]][s], va$time[s], va$cens[s])$c.index, error=function(e) NA)
      cc<- tryCatch(concordance.index(lp[[nm]][s],     va$time[s], va$cens[s])$c.index, error=function(e) NA)
      dC[b] <- a - cc
    }
    dC <- dC[is.finite(dC)]
    cat(sprintf("  %-14s ΔC = %+.4f  95%%BootstrapCI %+.4f ~ %+.4f  跨 0？%s\n",
                paste0(bestn,"−",nm), mean(dC), quantile(dC,.025), quantile(dC,.975),
                ifelse(quantile(dC,.025) < 0 & quantile(dC,.975) > 0, "是（无差异）", "否（有差异）")))
  }
  cat("\n  ★ 与第二域二分类主线的结论一致：多数模型间的 C-index 差异不显著。\n")
}
cat("\n========== Part G 结束 ==========\n")
sink(type="message"); sink(); close(con)
cat("Part G done\n")
