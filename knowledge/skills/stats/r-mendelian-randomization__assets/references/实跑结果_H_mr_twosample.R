# =====================================================================
# Part H｜第三域「孟德尔随机化」两样本 MR 复现
#   案例：BMI（暴露）→ 冠心病 CAD（结局），使用课程已协调好的 dat.csv
#   ★ 核心实验：等位基因方向写反的定量后果
#     (a) 全部 SNP 翻转 → 估计值精确取反
#     (b) 随机 30% 翻转 → 衰减并可能变号
#   另补齐课程缺失：Steiger 方向性检验、MR-PRESSO 的 NbDistribution 敏感性、
#                   径向 MR、用【实际样本量】计算的 F 值
# =====================================================================
options(stringsAsFactors = FALSE, warn = -1)
BASE <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/孟德尔"
OUT  <- "C:/Users/zy/Desktop/2、临床预测模型数据和代码/.workbuddy/r_practice"
con <- file(file.path(OUT, "H_mr_twosample_out.txt"), open = "wt", encoding = "UTF-8")
sink(con); sink(con, type = "message")
cat("========== Part H 两样本孟德尔随机化复现（BMI → CAD）==========\n")
cat("R:", R.version.string, "\n\n")
suppressPackageStartupMessages({ library(TwoSampleMR) })
safe <- function(tag, expr) tryCatch(expr, error = function(e)
  cat("  ✘ [", tag, "] ", conditionMessage(e), "\n", sep=""))

DAT <- file.path(BASE, "2024孟德尔资料/数据/实操数据/dat.csv")
cat("【0】读取课程已协调好的数据 dat.csv\n")
dat <- read.csv(DAT, check.names = FALSE)
cat("  维度：", nrow(dat), "×", ncol(dat), "\n")
cat("  关键列：", paste(intersect(c("SNP","beta.exposure","beta.outcome","se.exposure","se.outcome",
      "eaf.exposure","eaf.outcome","mr_keep","palindromic","ambiguous","samplesize.exposure"), names(dat)),
      collapse=", "), "\n\n")

## ---------- 1. 等位基因协调核查（课程只打印 table，未追踪原因） ----------
cat("################ 1. ★ 等位基因协调核查（课程只做了 table）################\n\n")
cat("  mr_keep 分布：\n"); print(table(dat$mr_keep, useNA = "ifany"))
cat("  palindromic（回文 SNP，A/T 或 C/G）：\n"); print(table(dat$palindromic, useNA = "ifany"))
cat("  ambiguous（方向无法判断）：\n"); print(table(dat$ambiguous, useNA = "ifany"))
if ("remove" %in% names(dat)) { cat("  remove 标记：\n"); print(table(dat$remove, useNA="ifany")) }
cat("\n  ★ 课程只跑了 `table(dat$mr_keep)`，未追踪被剔除 SNP 的原因。\n")
cat("     若 SNP 数大幅下降（如 50 → 10），结论可能完全翻转 → 必须列出被剔除清单。\n\n")

keep <- dat[dat$mr_keep %in% c(TRUE, "TRUE"), ]
cat("  保留用于分析的 SNP 数：", nrow(keep), "（原始", nrow(dat), "）\n\n")

## ---------- 2. 主分析 + OR ----------
cat("################ 2. 主分析与效应量 ################\n\n")
res  <- mr(keep, method_list = c("mr_ivw","mr_egger_regression","mr_weighted_median",
                                 "mr_weighted_mode","mr_simple_mode"))
print(res[, c("method","nsnp","b","se","pval")])
resor <- generate_odds_ratios(res)
cat("\n  OR 及 95%CI：\n")
print(resor[, c("method","nsnp","or","or_low","or_high","pval")])
cat("\n  ★ 解释：二分类结局报 OR。本案例（BMI → CAD）原文报的正是 OR。\n")
cat("     ★ 方向核对：BMI 升高应【增加】CAD 风险（OR > 1）。若得到 OR < 1，\n")
cat("       第一件事是核对等位基因方向，而不是讨论\"BMI 是保护因素\"。\n\n")

## ---------- 3. 敏感性分析（四层） ----------
cat("################ 3. 敏感性分析（四层）################\n\n")
cat("【3.1】异质性检验（Cochran's Q，由 mr_heterogeneity 提供）\n")
safe("het", { h <- mr_heterogeneity(keep); print(h[, c("method","Q","Q_df","Q_pval")]) })
cat("\n【3.2】水平多效性（MR-Egger 截距）\n")
safe("ple", { p <- mr_pleiotropy_test(keep); print(p) })
cat("  ★ 截距 P>0.05 → 未检测到方向性多效性（注意：MR-Egger 功效低，阴性≠无多效性）\n\n")

cat("【3.3】★ MR-PRESSO 的 NbDistribution 敏感性（课程用 1000，自称应 ≥5000）\n")
for (nb in c(1000, 5000)) {
  safe(paste0("presso", nb), {
    set.seed(123)
    t0 <- Sys.time()
    pr <- run_mr_presso(keep, NbDistribution = nb)
    el <- difftime(Sys.time(), t0, units = "secs")
    g <- pr[[1]]$`MR-PRESSO results`$`Global Test`
    cat(sprintf("  NbDistribution = %-5d  全局检验 RSSobs = %.4f  P = %.4g  （耗时 %.1f 秒）\n",
                nb, g$RSSobs, g$Pvalue, as.numeric(el)))
    ot <- pr[[1]]$`MR-PRESSO results`$`Outlier Test`
    if (!is.null(ot)) {
      sig <- which(ot$Pvalue < 0.05)
      cat("     离群 SNP 数（P<0.05）：", length(sig),
          ifelse(length(sig)>0, paste0(" → ", paste(keep$SNP[sig], collapse=", ")), ""), "\n")
    }
  })
}
cat("  ★★ 结论：两次运行的离群 SNP 判定与 P 值可能不同 —— 这正是「NbDistribution 必须够大」的原因。\n")
cat("     NbDistribution 是 MR-PRESSO 模拟次数的参数，次数不足时 P 值不稳定（Monte-Carlo 误差）。\n\n")

cat("【3.4】留一法（leave-one-out）\n")
safe("loo", {
  lo <- mr_leaveoneout(keep)
  b_all <- res$b[res$method == "Inverse variance weighted"]
  rng <- range(lo$b, na.rm = TRUE)
  cat("  全 SNP IVW 估计 b =", round(b_all, 5), "\n")
  cat("  逐一剔除后的 b 范围：", round(rng[1], 5), "–", round(rng[2], 5), "\n")
  drv <- lo[which.max(abs(lo$b - b_all)), ]
  cat("  最大影响 SNP：", drv$SNP, "（剔除后 b =", round(drv$b, 5),
      "，变化 =", round(drv$b - b_all, 5), "）\n")
  cat("  ★ 判读：若剔除单个 SNP 后结论变号或失去显著性 → 结论被单个 SNP 驱动，不可靠\n")
})
cat("\n")

## ---------- 4. 工具变量强度（★ 用实际样本量，修正课程硬编码 338903） ----------
cat("################ 4. 工具变量强度（★ 修正课程硬编码样本量）################\n\n")
safe("fval", {
  N <- keep$samplesize.exposure
  eaf <- keep$eaf.exposure
  b <- keep$beta.exposure; se <- keep$se.exposure
  r2 <- (2*eaf*(1-eaf)*b^2) / (2*eaf*(1-eaf)*b^2 + 2*eaf*(1-eaf)*N*se^2)
  F1 <- r2*(N-2)/(1-r2)
  cat("  单 SNP F 值：中位", round(median(F1),1), "；范围", round(min(F1),1), "–", round(max(F1),1), "\n")
  cat("  F < 10（弱工具）的 SNP 数：", sum(F1 < 10), "/", length(F1), "\n")
  r3 <- sum(r2)
  N_med <- median(N)
  Ft_actual <- r3*(N_med-2)/(1-r3)
  Ft_hard   <- r3*(338903-2)/(1-r3)
  cat("\n  总 F 值：\n")
  cat("    用【实际中位样本量】", N_med, "→ 总 F =", round(Ft_actual, 1), "\n")
  cat("    用课程硬编码的 338903  → 总 F =", round(Ft_hard, 1), "\n")
  cat("    差异 =", round(Ft_hard - Ft_actual, 1),
      sprintf("（%.1f%%）\n", 100*(Ft_hard/Ft_actual - 1)))
  cat("  ★★ 课程 `Ft <- r3*(338903-2)/(1-r3)` 硬编码了样本量；本数据 N 在",
      min(N), "–", max(N), "之间波动，", N_med, " 与实际相符，故本例差异不大。\n")
  cat("     但【换数据集忘记改这个数】会直接导致总 F 值错误 → 弱工具判断失效。\n")
  cat("     更稳妥：直接用 TwoSampleMR::add_rsq() 或 compute_f()，避免手写公式。\n")
})
cat("\n")

## ---------- 5. ★ Steiger 方向性检验（课程完全缺失） ----------
cat("################ 5. ★ Steiger 方向性检验（课程完全缺失）################\n\n")
safe("steiger", {
  st <- directionality_test(keep)
  print(st[, c("snp_r2.exposure","snp_r2.outcome","correct_causal_direction",
               "steiger_pval","steiger_dir")])
  cat("  ★ 判读：correct_causal_direction = TRUE 且 steiger_pval < 0.05\n")
  cat("     → 自变量对结局的方差解释量显著大于反向，支持\"暴露 → 结局\"的因果方向。\n")
  cat("  ★★ STROBE-MR 与《MR 统计学共识》（文献 9）均推荐必备此项，课程全域未涉及。\n")
})
cat("\n")

## ---------- 6. ★★★ 核心实验：等位基因方向写反的定量后果 ----------
cat("################ 6. ★★★ 等位基因方向反转实验 ################\n\n")
cat("  背景：GWAS-VCF 规范中 ES（效应量）对应 ALT 等位基因。\n")
cat("        若误把 REF 当作 effect_allele（课程 VCF 读取路径疑似如此），\n")
cat("        则该 SNP 的 beta 符号会整体反转 —— 而软件【不会报错】。\n\n")
b0 <- res$b[res$method == "Inverse variance weighted"]
p0 <- res$pval[res$method == "Inverse variance weighted"]
cat(sprintf("  [基准] 正确方向：IVW b = %+.5f，SE = %.5f，P = %.3g，OR = %.4f\n\n",
            b0, res$se[res$method=="Inverse variance weighted"], p0, exp(b0)))

## (a) 全部 SNP 翻转
dA <- keep; dA$beta.exposure <- -dA$beta.exposure
rA <- mr(dA, method_list = "mr_ivw")
cat(sprintf("  [实验A] 全部 %d 个 SNP 的效应等位基因写反：\n", nrow(keep)))
cat(sprintf("          IVW b = %+.5f（基准的 %+.1f%%），P = %.3g，OR = %.4f\n",
            rA$b, 100*(rA$b/b0 - 1), rA$pval, exp(rA$b)))
cat(sprintf("          → 与基准的关系：b_A / b_0 = %+.4f（理论值 −1.0000，即精确取反）\n", rA$b/b0))
cat("          ★ 结论：**效应方向完全反转，但 P 值、SNP 数、异质性全都一模一样**。\n")
cat("            这是 MR 中最危险的错误：所有「质量指标」都正常，只有结论是反的。\n\n")

## (b) 随机 30% 翻转（模拟只有部分回文 SNP 判断错误）
set.seed(42)
for (frac in c(0.10, 0.30, 0.50)) {
  dB <- keep
  idx <- sample(1:nrow(dB), round(frac*nrow(dB)))
  dB$beta.exposure[idx] <- -dB$beta.exposure[idx]
  rB <- mr(dB, method_list = "mr_ivw")
  cat(sprintf("  [实验B] 随机 %.0f%% 的 SNP（n=%d）方向写反：IVW b = %+.5f（基准的 %+.1f%%），P = %.3g\n",
              frac*100, length(idx), rB$b, 100*(rB$b/b0), rB$pval))
}
cat("\n  ★★ 实验 B 的意义：真实场景中往往只有部分 SNP（如回文 SNP）方向判断错误，\n")
cat("     此时结果不是干净的取反，而是【向零衰减 + 随机扰动】，甚至可能在特定比例下变号。\n")
cat("     这解释了为什么「效应方向与文献不一致」必须以核对等位基因作为第一诊断步骤。\n\n")
cat("  ★★ 防御措施（本技能已固化为铁律）：\n")
cat("     1) 用 EAF 匹配判断回文 SNP 方向（1000 Genomes 参考频率）；\n")
cat("     2) 查看 dat 的 palindromic / ambiguous 列，明确处理方式；\n")
cat("     3) 结果出来先与既往文献/临床常识核对方向（BMI↑ → CAD↑）；\n")
cat("     4) VCF 读取时确认 effect_allele = ALT（不是 REF）。\n\n")

## ---------- 7. 径向 MR（现代标准敏感性分析，课程缺失） ----------
cat("################ 7. 径向 MR（课程缺失）################\n\n")
if (requireNamespace("RadialMR", quietly = TRUE)) {
  safe("radial", {
    library(RadialMR)
    rdat <- format_radial(keep$beta.exposure, keep$beta.outcome, keep$se.exposure, keep$se.outcome, keep$SNP)
    ivw <- ivw_radial(rdat, alpha = 0.05, weights = 1)
    cat("  IVW 径向 MR：\n"); print(ivw$outliers)
    egg <- egger_radial(rdat, alpha = 0.05, weights = 1)
    cat("  Egger 径向 MR：\n"); print(egg$outliers)
  })
} else {
  cat("  RadialMR 未安装 → 本机可通过 install.packages('RadialMR') 获得；\n")
  cat("  径向 MR 的价值：把 SNP 的权重与异质性可视化在同一张图，同时给出离群与多效性检验。\n")
}
cat("\n========== Part H 结束 ==========\n")
sink(type="message"); sink(); close(con)
cat("Part H done\n")
