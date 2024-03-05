# Load necessary libraries
library(dplyr)
library(stringr)

###STATE BASED DATA

# List all CSV files
files <- list.files(pattern = "\\.csv$")

# Initialize an empty data frame to store combined data
combined_data <- data.frame()

# Loop through files, read, and combine
for (file in files) {
  # Read the file, skipping the first two rows
  temp_data <- read.csv(file, skip = 2, header = TRUE)
  
  # Extract year and search term from the file name
  year_from_file <- str_extract(file, "\\d{4}")
  search_term_from_file <- str_extract(file, "[^_]+(?=_\\d{4})") # Gets the text before '_year.csv'
  
  # Extract the original search term and year from the second column's name
  original_search_term <- gsub("[:].*", "", names(temp_data)[2]) # Remove everything after the colon
  year_from_column <- str_extract(names(temp_data)[2], "\\d{4}")
  
  # Check consistency and decide the year value (prefer column if available)
  year <- ifelse(!is.na(year_from_column) & year_from_column != "", year_from_column, year_from_file)
  
  # Rename columns to a standard name for merging
  names(temp_data) <- c("Region", "Search_Term_Value")
  
  cleaned_search_term <- gsub("\\..*", "", original_search_term)
  
  # Add year and search term columns
  temp_data$Year <- year
  temp_data$Search_Term <- cleaned_search_term
  
  # Combine with the main data frame
  combined_data <- bind_rows(combined_data, temp_data)
}

write.csv(combined_data, "search_state_based.csv" )


###US TRENDS

# List all CSV files related to US trends
files_US <- list.files(pattern = "_US\\.csv$")

# Initialize an empty data frame to store combined data
combined_data_US <- data.frame()

# Loop through files, read, and combine
for (file in files_US) {
  # Read the file, skipping the first two rows
  temp_data_US <- read.csv(file, skip = 2, header = TRUE)
  
  # Extract the search term from the second column's name (assuming format like 'Stress: (United States)')
  search_term_US <- gsub(":.*", "", names(temp_data_US)[2]) # Remove everything after the colon
  
  # Clean the search term by removing extra characters and replacing dots with spaces
  clean_search_term_US <- gsub("[.].*", "", search_term_US) # Remove everything after a dot
  clean_search_term_US <- gsub("[.]", " ", clean_search_term_US) # Replace remaining dots with spaces if any
  
  # Rename columns to a standard name for merging and ensure Trend_Value is treated as numeric
  names(temp_data_US) <- c("Month", "Trend_Value")
  temp_data_US$Trend_Value <- as.numeric(as.character(temp_data_US$Trend_Value)) # Convert Trend_Value to numeric
  
  # Handle possible conversion issues (NA for non-numeric strings)
  if(any(is.na(temp_data_US$Trend_Value))){
    warning(paste("NA introduced by coercion in file:", file))
  }
  
  # Add cleaned search term column
  temp_data_US$Search_Term <- clean_search_term_US
  
  # Combine with the main data frame
  combined_data_US <- bind_rows(combined_data_US, temp_data_US)
}

write.csv(combined_data_US, "search_US_trends.csv" )

