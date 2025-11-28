# This script defines the precmd hook to dynamically update the prompt 
# when entering a nix-shell environment, based on the NIX_CONTEXT_DISPLAY variable.

# Ensure Zsh functionality is loaded
autoload -U add-zsh-hook

nix_indicator_precmd() {
  # Check if we are inside a Nix shell
  if [[ -n "$IN_NIX_SHELL" ]]; then
     local nix_command="SHELL" # Default context
     
     if [[ -n "$NIX_CONTEXT_DISPLAY" ]]; then
       # Remove leading flags/options to simplify display for the indicator
       # Using 'sed' for substitution is more reliable in Zsh contexts.
       local raw_context="$NIX_CONTEXT_DISPLAY"
       raw_context=$(echo "$raw_context" | sed -E 's/^-p\s*//; s/--packages\s*//; s/^-//')
       
       if [[ ${#raw_context} -le 20 ]]; then
           # Use the simple context if it's short
           nix_command="$raw_context"
       else
           # Truncate and show the end of the context if it's too long
           nix_command="...${raw_context: -17}"
       fi
     fi

     # Construct the indicator (e.g., [NIX:cowsay] or [NIX:pnpm v8])
     local indicator="%F{red}[NIX:$nix_command]%f "
       
     # Append indicator to the prompt
     PS1="$PS1$indicator"
  fi
}

# Register the hook to run before every prompt
add-zsh-hook precmd nix_indicator_precmd
