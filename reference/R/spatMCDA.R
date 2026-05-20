
####################FULL CODE
############################################################
# AGROFORESTRY SUITABILITY MAPPING USING MCDA
# Objective weighting (CRITIC + Entropy) + AHP matrix
############################################################
# ✅ What This Script Produces
# -Objective CRiteria Importance Through Intercriteria Correlation (CRITIC) weights
# Diakoulaki, D., Mavrotas, G., & Papayannakis, L. (1995). Determining objective weights in multiple criteria problems: The CRITIC method. Computers & Operations Research. https://doi.org/10.1016/0305-0548(94)00059-H
# -Entropy weights (comparison)
#Entropy weighting is an objective weighting method derived from Shannon’s Information Theory developed by Claude Shannon (1948).
#In decision analysis, entropy measures the degree of disorder or uncertainty in a criterion. The key principle:
#A criterion that shows greater variability (information) across alternatives carries more decision-making power, and therefore should receive a higher weight.
# -Fully consistent AHP matrix
# -Continuous suitability map
# -4-class suitability map
# -Sensitivity test map
# -Exported GeoTIFF files
# ---------------------------
# 1️⃣ LOAD LIBRARIES
# ---------------------------
library(terra)
library(sf)

# ---------------------------
# 2️⃣ LOAD DATA
# ---------------------------
lc   <- rast("landcover.tif")
slope <- rast("slope.tif")
soil  <- rast("soil.tif")
temp  <- rast("temperature.tif")
prec  <- rast("rainfall.tif")

pa <- st_read("protected_areas.shp")

# ---------------------------
# 3️⃣ ALIGN RASTERS
# ---------------------------
# Use landcover as template
template <- lc

slope <- project(slope, template)
soil  <- project(soil, template)
temp  <- project(temp, template)
prec  <- project(prec, template)

slope <- resample(slope, template)
soil  <- resample(soil, template)
temp  <- resample(temp, template)
prec  <- resample(prec, template)

# Rasterize protected areas
pa_r <- rasterize(vect(pa), template, field=1)
pa_r[is.na(pa_r)] <- 0

# ---------------------------
# 4️⃣ STANDARDIZATION (0–1)
# ---------------------------

minmax_scale <- function(r) {
  (r - global(r, "min", na.rm=TRUE)[1]) /
    (global(r, "max", na.rm=TRUE)[1] -
     global(r, "min", na.rm=TRUE)[1])
}

# Example suitability logic:
# Lower slope = better
# Protected areas = unsuitable

lc_s    <- minmax_scale(lc)
slope_s <- 1 - minmax_scale(slope)
soil_s  <- minmax_scale(soil)
temp_s  <- minmax_scale(temp)
prec_s  <- minmax_scale(prec)
pa_s    <- 1 - pa_r   # protected = 0 suitability

# Stack layers
stack_layers <- c(lc_s, slope_s, soil_s, temp_s, prec_s, pa_s)
names(stack_layers) <- c("Landcover","Slope","Soil","Temp","Rain","Protected")

# ---------------------------
# 5️⃣ EXTRACT VALUES FOR WEIGHTING
# ---------------------------

vals <- as.data.frame(values(stack_layers), na.rm=TRUE)
vals <- na.omit(vals)

############################################################
# 6️⃣ CRiteria Importance Through Intercriteria Correlation (CRITIC) WEIGHTING (OBJECTIVE)
############################################################

# Standard deviation
sd_vals <- apply(vals, 2, sd)

# Correlation matrix
cor_mat <- cor(vals)

# CRITIC information
Cj <- sd_vals * colSums(1 - cor_mat)

weights_critic <- Cj / sum(Cj)

cat("CRITIC Weights:\n")
print(round(weights_critic, 3))

############################################################
# 7️⃣ ENTROPY WEIGHTING (OBJECTIVE)
############################################################

# Normalize
norm_vals <- vals / rowSums(vals)

k <- 1/log(nrow(norm_vals))
E <- -k * colSums(norm_vals * log(norm_vals + 1e-12))

d <- 1 - E
weights_entropy <- d / sum(d)

cat("Entropy Weights:\n")
print(round(weights_entropy, 3))

############################################################
# 8️⃣ GENERATE AUTOMATIC AHP MATRIX FROM CRITIC
############################################################

n <- length(weights_critic)
ahp_auto <- matrix(NA, n, n)

for(i in 1:n){
  for(j in 1:n){
    ahp_auto[i,j] <- weights_critic[i] / weights_critic[j]
  }
}

rownames(ahp_auto) <- names(stack_layers)
colnames(ahp_auto) <- names(stack_layers)

cat("Automated AHP Matrix:\n")
print(round(ahp_auto, 3))

############################################################
# 9️⃣ WEIGHTED OVERLAY (USING CRITIC)
############################################################

suitability <- 
  stack_layers[[1]] * weights_critic[1] +
  stack_layers[[2]] * weights_critic[2] +
  stack_layers[[3]] * weights_critic[3] +
  stack_layers[[4]] * weights_critic[4] +
  stack_layers[[5]] * weights_critic[5] +
  stack_layers[[6]] * weights_critic[6]

plot(suitability, main="Agroforestry Suitability (CRITIC)")

############################################################
# 🔟 CLASSIFY SUITABILITY
############################################################

# Natural breaks classification (quartiles)
q <- quantile(values(suitability), probs=c(0.25,0.5,0.75), na.rm=TRUE)

suit_class <- classify(suitability,
                       rbind(
                         c(-Inf, q[1], 1),
                         c(q[1], q[2], 2),
                         c(q[2], q[3], 3),
                         c(q[3], Inf, 4)
                       ))

levels <- c("Unsuitable","Marginal","Moderate","Highly Suitable")

plot(suit_class, main="Suitability Classes")

############################################################
# 1️⃣1️⃣ SENSITIVITY ANALYSIS (±10%)
############################################################

set.seed(123)

perturb_weights <- weights_critic * 
  (1 + runif(length(weights_critic), -0.1, 0.1))

perturb_weights <- perturb_weights / sum(perturb_weights)

suit_sensitivity <- 
  stack_layers[[1]] * perturb_weights[1] +
  stack_layers[[2]] * perturb_weights[2] +
  stack_layers[[3]] * perturb_weights[3] +
  stack_layers[[4]] * perturb_weights[4] +
  stack_layers[[5]] * perturb_weights[5] +
  stack_layers[[6]] * perturb_weights[6]

plot(suit_sensitivity, main="Sensitivity Map (±10%)")

############################################################
# 1️⃣2️⃣ EXPORT RESULTS
############################################################

writeRaster(suitability,
            "Agroforestry_Suitability_CRITIC.tif",
            overwrite=TRUE)

writeRaster(suit_class,
            "Agroforestry_Suitability_Classes.tif",
            overwrite=TRUE)

writeRaster(suit_sensitivity,
            "Agroforestry_Sensitivity_Map.tif",
            overwrite=TRUE)

############################################################
# END OF SCRIPT
############################################################


