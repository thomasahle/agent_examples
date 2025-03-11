#!/bin/bash
# Script to run all agent evaluations and visualize results

# Set up environment
export AUTOMATED_EVALUATION=1
OUTPUT_DIR="outputs"
RESULTS_FILE="$OUTPUT_DIR/agent_bug_evaluation_results.json"
CODEBASE_PATH="test_codebase"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to check if OpenAI API key is set
check_api_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}Error: OPENAI_API_KEY environment variable is not set.${NC}"
        echo "Please set your OpenAI API key with:"
        echo "  export OPENAI_API_KEY=your_api_key_here"
        exit 1
    fi
}

# Run the evaluations
run_evaluations() {
    echo -e "${GREEN}Starting agent evaluations...${NC}"
    
    # Run the evaluation harness
    python3.12 -m eval.harness --codebase "$CODEBASE_PATH" --output "$RESULTS_FILE"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Evaluation failed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Evaluations completed successfully.${NC}"
}

# Generate visualizations
generate_visualizations() {
    echo -e "${GREEN}Generating visualizations...${NC}"
    
    # Run visualization script
    python3.12 ./visualize_results.py --input "$RESULTS_FILE" \
                           --output-bar "$OUTPUT_DIR/agent_comparison_bar.png" \
                           --output-radar "$OUTPUT_DIR/agent_comparison_radar.png"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Visualization generation failed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Visualizations generated successfully.${NC}"
    echo -e "Bar chart: ${YELLOW}$OUTPUT_DIR/agent_comparison_bar.png${NC}"
    echo -e "Radar chart: ${YELLOW}$OUTPUT_DIR/agent_comparison_radar.png${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}=== Agent Bug Finder Evaluation ===${NC}"
    check_api_key
    run_evaluations
    generate_visualizations
    echo -e "${GREEN}All tasks completed successfully.${NC}"
    echo -e "Evaluation results: ${YELLOW}$RESULTS_FILE${NC}"
}

# Run the main function
main