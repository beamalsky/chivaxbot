# Author: Charmaine Runes
# For South Side Weekly
# Project: ChiVaxBot - Time Series

library(tidyverse)
library(tidyr)
library(dplyr)
library(readr)
library(ggplot2)
library(scales)
library(stringr)
library(here)
library(zoo)
library(ggtext)
library(httr)
library(jsonlite)

res = GET("https://data.cityofchicago.org/resource/553k-3xzc.json?$limit=10000")
data = fromJSON(rawToChar(res$content))

# Merge with manual crosswalk
crosswalk <- read_csv("data/zip-cityside-crosswalk.csv", col_types=cols(.default="c")) %>% 
  mutate(zip_code = zip) %>% 
  select(zip_code, side) 

data.clean <- data %>% 
  mutate(date = as.Date(substr(date, 1, 10)),
         `_1st_dose_percent_population` = as.numeric(`_1st_dose_percent_population`)) 

data.merged <- merge(data.clean, crosswalk, by.x="zip_code", by.y="zip_code")

southside <- data.merged %>% 
  filter(side == "South")

rest <- data.merged %>% 
  filter(side != "South")

# Plot time-series
ggplot(data=rest, aes(date, `_1st_dose_percent_population`, group=zip_code)) +
    geom_line(color="lightgrey", alpha=0.7) +
    geom_line(data=southside, color="orange", alpha=0.7) +
    xlab("Date") + ylab("Percent of pop. received first dose") +
    scale_y_continuous(labels = scales::percent_format(accuracy=1), 
                       breaks=seq(0, 1, 0.1)) +
    scale_color_brewer(palette = "Dark2") + 
    theme(
      axis.ticks = element_blank(),
      panel.grid.major.y = element_line(size=0.5, linetype="dotted", colour ="lightgrey"),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.border = element_blank(),
      panel.background = element_rect(fill = "white", colour = "white"))

# Plot time-series
ggplot(data=data.merged, aes(date, `_1st_dose_percent_population`, group=zip_code)) +
  geom_line(aes(color=side), alpha=0.7) +
  xlab("Date") + ylab("Percent of pop. received first dose") +
  scale_y_continuous(labels = scales::percent_format(accuracy=1), 
                     breaks=seq(0, 1, 0.1)) +
  scale_color_brewer(palette = "Dark2") + 
  theme(
    axis.ticks = element_blank(),
    panel.grid.major.y = element_line(size=0.5, linetype="dotted", colour ="lightgrey"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    panel.background = element_rect(fill = "white", colour = "white"))
