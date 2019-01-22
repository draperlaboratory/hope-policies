#ifndef CGI_UTIL_H
#define CGI_UTIL_H

#include "user.h"
#include "auth.h"
#include "cgic.h"

#define CGI_SESSION_COOKIE_SIZE AUTH_SESSION_ID_SIZE
#define SECONDS_IN_DAY 86400

typedef enum {
  CGI_FORM_GET,
  CGI_FORM_POST,
} form_type_t;

bool GetActiveUser(user_t **user, bool mock);
void SimpleCookie(char *name, char *value);
void InitializeCgiHeader(void);
void FormStart(form_type_t form_type, const char *destination);
void FormEnd(void);
void Whitespace(size_t size);

user_t *GetSessionUser(void);
void AutoRedirect(char *destination, float duration, char *message);

#endif // CGI_UTIL_H
