# --- PART 1: DATA & MODEL ---
library("rENA")
library("plotly")
library("htmlwidgets")

data("RS.data")
codeNames <- c("Data", "Technical.Constraints", "Performance.Parameters", 
               "Client.and.Consultant.Requests", "Design.Reasoning", "Collaboration")

accum <- ena.accumulate.data(
  units = RS.data[,c("Condition","UserName")],
  conversation = RS.data[,c("Condition","GroupName")],
  metadata = RS.data[,c("GroupName", "Condition", "UserName")],
  codes = RS.data[,codeNames],
  window.size.back = 4
)
set <- ena.make.set(enadata = accum)

# --- PART 2: COORDINATES ---
get_coords <- function(mat) {
  df <- as.data.frame(as.matrix(mat))
  if(ncol(df) < 3) { df[[3]] <- 0 } 
  df <- df[, 1:3]
  colnames(df) <- c("X", "Y", "Z")
  return(df)
}
node_coords <- get_coords(set$rotation$nodes)
plot_data   <- get_coords(set$points)
plot_data$Condition <- as.character(set$meta.data$Condition)
plot_data$UserName  <- as.character(set$meta.data$UserName)

# --- PART 3: WEIGHTS ---
first_w  <- colMeans(set$line.weights[set$meta.data$Condition == "FirstGame", ])
second_w <- colMeans(set$line.weights[set$meta.data$Condition == "SecondGame", ])
sub_w    <- first_w - second_w

# --- PART 4: THE PLOT ---
fig <- plot_ly()

# 1. NODES
for(i in 1:nrow(node_coords)) {
  fig <- fig %>% add_trace(
    x = node_coords$X[i], y = node_coords$Y[i], z = node_coords$Z[i],
    type = "scatter3d", mode = "markers+text",
    text = codeNames[i], name = codeNames[i], legendgroup = "Codes",
    textposition = "top center",
    marker = list(size = 6, color = "black"),
    textfont = list(family = "Arial Black", size = 11)
  )
}

# 2. NETWORK LINES (RGBA for Transparency)
# Red at 70% opacity: rgba(255, 23, 68, 0.7)
# Cyan at 70% opacity: rgba(0, 229, 255, 0.7)

fig <- fig %>% add_trace(
  x = c(NA), y = c(NA), z = c(NA), type = "scatter3d", mode = "lines",
  line = list(color = "rgba(255, 23, 68, 0.7)", width = 12),
  name = "FirstGame Stronger", legendgroup = "Lines"
)
fig <- fig %>% add_trace(
  x = c(NA), y = c(NA), z = c(NA), type = "scatter3d", mode = "lines",
  line = list(color = "rgba(0, 229, 255, 0.7)", width = 12),
  name = "SecondGame Stronger", legendgroup = "Lines"
)

# 3. ACTUAL NETWORK LINES
num_nodes <- nrow(node_coords)
for(i in 1:(num_nodes-1)) {
  for(j in (i+1):num_nodes) {
    idx <- (i-1)*(num_nodes - i/2) + (j-i)
    val <- sub_w[idx]
    if(!is.na(val) && abs(val) > 0.02) {
      fig <- fig %>% add_trace(
        x = c(node_coords$X[i], node_coords$X[j]),
        y = c(node_coords$Y[i], node_coords$Y[j]),
        z = c(node_coords$Z[i], node_coords$Z[j]),
        type = "scatter3d", mode = "lines",
        line = list(
          width = abs(val) * 85, 
          color = if(val > 0) "rgba(255, 23, 68, 0.7)" else "rgba(0, 229, 255, 0.7)"
        ),
        showlegend = FALSE,
        legendgroup = "Lines"
      )
    }
  }
}

# 4. STUDENTS
student_colors <- c("FirstGame" = "rgba(157, 0, 255, 0.5)", 
                    "SecondGame" = "rgba(128, 128, 128, 0.😎") 

for(cond in unique(plot_data$Condition)) {
  d_sub <- plot_data[plot_data$Condition == cond,]
  fig <- fig %>% add_trace(
    x = d_sub$X, y = d_sub$Y, z = d_sub$Z,
    type = "scatter3d", mode = "markers",
    name = paste("Students:", cond),
    legendgroup = "Students",
    marker = list(size = 4, color = student_colors[cond]),
    text = d_sub$UserName, hoverinfo = "text"
  )
}

# --- PART 5: LAYOUT (With Meaningful Dimension Titles) ---
fig <- fig %>% layout(
  title = list(
    text = "<b>3D Epistemic Network Comparison</b><br><sup>Visualizing Cognitive Connections & Professional Discourse</sup>",
    y = 0.95
  ),
  scene = list(
    xaxis = list(
      title = "<b>X: Procedural vs. Social</b>", 
      type = "linear",
      backgroundcolor = "rgb(240, 240, 240)",
      showbackground = TRUE
    ),
    yaxis = list(
      title = "<b>Y: Constraints vs. Creativity</b>", 
      type = "linear",
      backgroundcolor = "rgb(230, 230, 230)",
      showbackground = TRUE
    ),
    zaxis = list(
      title = "<b>Z: System Complexity</b>", 
      type = "linear",
      backgroundcolor = "rgb(220, 220, 220)",
      showbackground = TRUE
    ),
    aspectmode = "data"
  ),
  margin = list(l=0, r=0, b=0, t=80)
)

fig

saveWidget(fig, "Final_3D_ENA_Comparison.html", selfcontained = TRUE)