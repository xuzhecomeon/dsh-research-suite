## =============================================================
## R 端到端能力验证：临床统计 + 绘图（模拟数据，不含任何真实患者信息）
## =============================================================
suppressPackageStartupMessages({
  library(data.table); library(tableone); library(ggplot2)
  library(pROC); library(survival); library(survminer); library(patchwork)
})

set.seed(20260915)
n <- 300
d <- data.table(
  group    = factor(sample(c("\u6807\u51c6\u6cbb\u7597", "\u5f3a\u5316\u6cbb\u7597"), n, TRUE)),
  age      = round(rnorm(n, 62, 14)),
  sex      = factor(sample(c("\u7537", "\u5973"), n, TRUE)),
  sofa     = round(rnorm(n, 8, 3)),
  lactate  = round(rlnorm(n, log(2.4), 0.5), 2),
  mv       = factor(sample(c("\u5426", "\u662f"), n, TRUE)),
  vaso     = factor(sample(c("\u5426", "\u662f"), n, TRUE))
)
lp <- -4.6 + 0.045 * d$age + 0.26 * d$sofa + 0.42 * d$lactate +
  0.65 * (d$mv == "\u662f") + 0.75 * (d$vaso == "\u662f") - 0.55 * (d$group == "\u5f3a\u5316\u6cbb\u7597")
d$death <- rbinom(n, 1, plogis(lp))
d$time  <- round(rweibull(n, shape = 1.4, scale = 40 * exp(-0.5 * (d$death == 1))))

out <- c()
P <- function(...) { s <- paste0(...); out <<- c(out, s); cat(s, "\n") }

P("### 1. \u57fa\u7ebf\u7279\u5f81\u8868\uff08Table 1\uff09")
vars <- c("age", "sex", "sofa", "lactate", "mv", "vaso")
tb <- CreateTableOne(vars = vars, strata = "group", data = d, test = TRUE)
print(tb, showAllLevels = TRUE, formatOptions = list(big.mark = ","))
tbm <- print(tb, showAllLevels = TRUE, quote = FALSE, noSpaces = TRUE, printToggle = FALSE)
write.csv(tbm, "_demo_table1.csv", fileEncoding = "UTF-8")
out <- c(out, capture.output(print(tb, showAllLevels = TRUE)))

P("\n### 2. \u7ec4\u95f4\u6bd4\u8f83\uff08t \u68c0\u9a8c / \u5361\u65b9\uff09")
for (v in c("age", "sofa", "lactate")) {
  tt <- t.test(d[[v]] ~ d$group)
  g1 <- d[d$group == "\u6807\u51c6\u6cbb\u7597"][[v]]
  g2 <- d[d$group == "\u5f3a\u5316\u6cbb\u7597"][[v]]
  P(sprintf("  %-8s mean\u00b1SD: %.2f\u00b1%.2f vs %.2f\u00b1%.2f ; t=%.2f, P=%.4f",
            v, mean(g1), sd(g1), mean(g2), sd(g2), tt$statistic, tt$p.value))
}
for (v in c("sex", "mv", "vaso")) {
  cs <- chisq.test(table(d[[v]], d$group))
  P(sprintf("  %-8s chi2=%.2f, df=%d, P=%.4f", v, cs$statistic, cs$parameter, cs$p.value))
}

P("\n### 3. \u591a\u56e0\u7d20 Logistic \u56de\u5f52\uff08\u7ed3\u5c40\uff1a28 \u5929\u6b7b\u4ea1\uff09")
fit <- glm(death ~ group + age + sex + sofa + lactate + mv + vaso, data = d, family = binomial)
sm <- summary(fit)$coefficients
or_tab <- data.table(
  term = rownames(sm),
  OR   = exp(sm[, 1]),
  lo   = exp(sm[, 1] - 1.96 * sm[, 2]),
  hi   = exp(sm[, 1] + 1.96 * sm[, 2]),
  P    = sm[, 4]
)
label_map <- c("group\u5f3a\u5316\u6cbb\u7597" = "\u5f3a\u5316\u6cbb\u7597 vs \u6807\u51c6\u6cbb\u7597",
               "age" = "\u5e74\u9f84", "sex\u5973" = "\u5973\u6027", "sofa" = "SOFA \u8bc4\u5206",
               "lactate" = "\u4e73\u9178", "mv\u662f" = "\u673a\u68b0\u901a\u6c14", "vaso\u662f" = "\u8840\u7ba1\u6d3b\u6027\u836f\u7269",
               "(Intercept)" = "\u5e38\u6570\u9879")
or_tab[, var := ifelse(term %chin% names(label_map), label_map[term], term)]
or_tab <- or_tab[var != "\u5e38\u6570\u9879"]
P(sprintf("  AUC\uff08\u6a21\u578b\u9884\u6d4b\u6982\u7387\uff09= %.3f", auc(d$death, fitted(fit))))
out <- c(out, capture.output(print(or_tab[, .(var, OR = round(OR, 2), lo = round(lo, 2), hi = round(hi, 2), P = signif(P, 3))])))
write.csv(or_tab, "_demo_or.csv", row.names = FALSE, fileEncoding = "UTF-8")

P("\n### 4. ROC \u8bc4\u4ef7")
r <- roc(d$death, fitted(fit), quiet = TRUE)
ci <- ci.auc(r)
P(sprintf("  AUC = %.3f (95%%CI %.3f-%.3f)", ci[2], ci[1], ci[3]))
best <- coords(r, "best", ret = c("threshold", "sensitivity", "specificity"), transpose = FALSE)
P(sprintf("  \u6700\u4f73\u9608\u503c = %.3f, \u654f\u5ea6 = %.1f%%, \u7279\u5f02\u5ea6 = %.1f%%",
          best$threshold, best$sensitivity * 100, best$specificity * 100))

P("\n### 5. Kaplan-Meier \u751f\u5b58\u5206\u6790")
km <- survfit(Surv(time, death) ~ group, data = d)
lr <- survdiff(Surv(time, death) ~ group, data = d)
P(sprintf("  Log-rank chi2 = %.2f, df = %d, P = %.4f", lr$chisq, length(lr$n) - 1, 1 - pchisq(lr$chisq, length(lr$n) - 1)))
cox <- coxph(Surv(time, death) ~ group + sofa + lactate, data = d)
cx <- summary(cox)
P(sprintf("  \u6821\u6b63\u540e HR\uff08\u5f3a\u5316 vs \u6807\u51c6\uff09= %.2f (95%%CI %.2f-%.2f), P = %.4f",
          cx$conf.int[1, 1], cx$conf.int[1, 3], cx$conf.int[1, 4], cx$coefficients[1, 5]))

## ---------------- \u51fa\u56fe ----------------
or_tab[, sig := ifelse(lo > 1 | hi < 1, "\u663e\u8457", "\u4e0d\u663e\u8457")]
or_tab[, dir := ifelse(OR >= 1, "\u98ce\u9669\u589e\u52a0", "\u4fdd\u62a4\u56e0\u7d20")]
p_forest <- ggplot(or_tab, aes(x = OR, y = reorder(var, OR))) +
  geom_vline(xintercept = 1, linetype = 2, colour = "grey55") +
  geom_errorbarh(aes(xmin = lo, xmax = hi), height = 0.18, linewidth = 0.7, colour = "grey30") +
  geom_point(aes(colour = dir), size = 3.2) +
  scale_x_log10(breaks = c(0.25, 0.5, 1, 2, 4, 8)) +
  scale_colour_manual(values = c("\u98ce\u9669\u589e\u52a0" = "#D6473F", "\u4fdd\u62a4\u56e0\u7d20" = "#2E8B57")) +
  labs(title = "A  \u591a\u56e0\u7d20 Logistic \u56de\u5f52\uff08OR, 95%CI\uff09", x = "OR\uff08\u5bf9\u6570\u5c3a\u5ea6\uff09", y = NULL, colour = NULL) +
  theme_classic(base_size = 11) +
  theme(legend.position = "bottom", plot.title = element_text(face = "bold"))

p_roc <- ggplot(data.frame(fpr = rev(1 - r$specificities), tpr = r$sensitivities),
                aes(fpr, tpr)) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, colour = "grey60") +
  geom_line(colour = "#D6473F", linewidth = 1) +
  annotate("text", x = 0.62, y = 0.12, size = 3.6,
           label = sprintf("AUC = %.3f\n95%%CI %.3f\u2013%.3f", ci[2], ci[1], ci[3])) +
  labs(title = "B  \u9884\u6d4b\u6a21\u578b ROC \u66f2\u7ebf", x = "1 - \u7279\u5f02\u5ea6", y = "\u7075\u654f\u5ea6") +
  coord_equal() + theme_classic(base_size = 11) +
  theme(plot.title = element_text(face = "bold"))

p_km <- ggsurvplot(km, data = d, pval = TRUE, conf.int = TRUE, risk.table = FALSE,
                   palette = c("#5B8FF9", "#D6473F"), size = 1,
                   legend.title = "", legend.labs = levels(d$group),
                   xlab = "\u968f\u8bbf\u65f6\u95f4\uff08\u5929\uff09", ylab = "\u751f\u5b58\u7387",
                   ggtheme = theme_classic(base_size = 11),
                   censor.size = 2)$plot +
  labs(title = "C  Kaplan-Meier \u751f\u5b58\u66f2\u7ebf") +
  theme(plot.title = element_text(face = "bold"), legend.position = c(0.82, 0.9))

fig <- (p_forest | (p_roc / p_km)) + plot_layout(widths = c(1, 1)) +
  plot_annotation(title = "\u4e34\u5e8a\u6570\u636e\u7edf\u8ba1\u4e0e\u7ed8\u56fe\u5168\u6d41\u7a0b\u9a8c\u8bc1\uff08\u6a21\u62df\u6570\u636e n=300\uff09",
                  theme = theme(plot.title = element_text(face = "bold", size = 13)))
ggsave("_demo_figure.png", fig, width = 12, height = 6.6, dpi = 300)
P(sprintf("\n\u56fe\u5df2\u751f\u6210: _demo_figure.png (%.0f KB)", file.info("_demo_figure.png")$size / 1024))
writeLines(out, "_demo_results.txt", useBytes = TRUE)
cat("\nALL_DONE\n")
