#Libraries
library(tidyverse)

#WD
setwd("~/Documents/GitHub/BMI706/Data/Raw Data/CDC Mortality")

####Read Data
#List all CSV files in the directory
path <- getwd()
file_names <- list.files(path, pattern = "*.txt", full.names = TRUE)

test <- read_delim("all_cause.txt",delim="\t")

# Function to read CSV and add a column with the file name
read_and_add_filename <- function(file_path) {
  file_name <- tools::file_path_sans_ext(basename(file_path))
  # Use read_delim with tab as the delimiter
  read_delim(file_path, delim = "\t",col_types = "-ffnfffffffnnnnnnn",escape_double = FALSE, col_names = TRUE, trim_ws = TRUE) %>%
    mutate(cause_of_death = file_name)
}

# Read all files, add FileName column, and combine into one dataframe
combined_df <- map_df(file_names, read_and_add_filename)

#Replace Na in death column with 0
combined_df <- combined_df %>% mutate(Deaths = replace_na(Deaths,0))

#Clean Up Cause of Death Columns
combined_df <- combined_df %>% mutate(cause_of_death = str_replace(cause_of_death,"all_cause_2","all_cause"))
combined_df$cause_of_death <- as.factor(combined_df$cause_of_death)

combined_df <- combined_df %>%
  mutate(cause_of_death = str_replace_all(cause_of_death, "_", " "),  # Replace underscores with spaces
         cause_of_death = str_to_title(cause_of_death))  # Convert to title case

# Optional: Write the combined dataframe to a new CSV file
write_csv(combined_df, "mortality_data.csv")
