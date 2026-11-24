#include <cstddef>
#include <string>

auto slashes = "a // b"; // after a string with slashes
char quote = '"'; // after a double quote in a character literal
char apostrophe = '\''; // after an escaped apostrophe
auto backslash = "\\"; // after an escaped backslash

auto raw = R"(a // b)"; // after a raw string with slashes
auto delimited = R"--(a )" // b)--"; // after a raw string whose text has a parenthesis and a quote
auto utf8_raw = u8R"x(a */ b)x"; // after a UTF-8 raw string with a block closer
auto wide_raw = LR"(/* a)"; // after a wide raw string with a block opener
auto utf16_raw = uR"(\)"; // after a raw string that ends in a backslash
auto utf32_raw = UR"(")"; // after a raw string of one quote
auto multiline = R"sql(
  SELECT 1; -- a SQL comment
  /* a block in the SQL */
  // two slashes in the SQL
)sql"; // after a raw string over several lines
auto spliced_raw = R"(a\
// b)"; // after a raw string with a backslash at the end of a line
auto not_raw = FOOR"(x)" "y"; // after an identifier that ends in R then a string

auto million = 1'000'000; // after digit separators
auto mask = 0x1'FF; // after a separator in a hex number
auto bits = 0b1010'1010u; // after a separator in a binary number
auto exponent = 1e1'0; // after a separator in an exponent
auto mixed = 0x1'FF + 'a'; // after a number then a character
auto wide = L'x'; // after a wide character
auto utf16 = u'x'; // after a UTF-16 character
auto utf32 = U'x'; // after a UTF-32 character
auto utf8 = u8'x'; // after a UTF-8 character
auto multichar = 'ab'; // after a character literal of two characters

constexpr std::size_t operator""_km(unsigned long long value) { return value; }
constexpr char operator""_c(char value) { return value; }
auto distance = 12'000_km; // after a user-defined literal with a separator
auto suffixed = '/'_c; // after a character with a suffix
auto text = std::string("//") + "/*"; // after strings of comment openers
auto slashes_char = '//'; // after a character literal of two slashes
auto unicode = "日本 // 語"; // after a UTF-8 string: naïve café
/* it's a block comment with an apostrophe */ int after_block = 0; // after the block comment
// it's a line comment with an apostrophe and a "quote
int after_quotes = 0; // after the line comment
auto empty = ""; auto adjacent = L"" "/*"; // after an empty string and a wide string
