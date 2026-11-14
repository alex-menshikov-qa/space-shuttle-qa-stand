# Space Shuttle Inc bug reports. API

Found with the Check List API: registering an autopilot, deleting it, getting an order by its tracking number.

| ID | Priority | Summary |
|---|---|---|
| SSI-29 | Medium | 201 Created when `login` is in Cyrillic |
| SSI-30 | Medium | 201 Created when `login` is in Chinese characters |
| SSI-31 | Medium | 201 Created when `login` is 1 character long |
| SSI-32 | Medium | 201 Created when `login` is 11 characters long |
| SSI-33 | Medium | 201 Created when `login` is 12 characters long |
| SSI-34 | Medium | 201 Created when `login` is a very long string |
| SSI-35 | Medium | 201 Created when `login` starts with a space |
| SSI-36 | Medium | 201 Created when `login` ends with a space |
| SSI-37 | Medium | 201 Created when `login` has a space in the middle |
| SSI-38 | Medium | 201 Created when `login` is a number |
| SSI-39 | Critical | 500 Internal Server Error when `login` is sent as `true` |
| SSI-40 | Medium | 201 Created when `login` consists of special characters |
| SSI-41 | Medium | 201 Created when `password` is 3 digits long |
| SSI-42 | Medium | 201 Created when `password` is 5 digits long |
| SSI-43 | Medium | 201 Created when `password` is a very long string |
| SSI-44 | Medium | 201 Created when `password` is sent without quotes |
| SSI-45 | Medium | 201 Created when `password` starts with a space |
| SSI-46 | Medium | 201 Created when `password` ends with a space |
| SSI-47 | Medium | 201 Created when `password` has a space in the middle |
| SSI-48 | Medium | 201 Created when `password` consists of letters |
| SSI-49 | Medium | 201 Created when `password` is `true` |
| SSI-50 | Medium | 201 Created when `password` consists of special characters |
| SSI-51 | Medium | 201 Created when `firstName` is in Chinese characters |
| SSI-52 | Medium | 201 Created when `firstName` is 1 character long |
| SSI-53 | Medium | 201 Created when `firstName` is 11 characters long |
| SSI-54 | Medium | 201 Created when `firstName` is 12 characters long |
| SSI-55 | Medium | 201 Created when `firstName` is a very long string |
| SSI-56 | Medium | 201 Created when `firstName` consists of digits |
| SSI-57 | Medium | 201 Created when `firstName` starts with a space |
| SSI-58 | Medium | 201 Created when `firstName` has a space in the middle |
| SSI-59 | Medium | 201 Created when `firstName` ends with a space |
| SSI-60 | Medium | 201 Created when `firstName` is `true` |
| SSI-61 | Medium | 201 Created when `firstName` consists of special characters |
| SSI-62 | Critical | Orders of a deleted autopilot are not removed |

---

<a id="ssi-29"></a>

## SSI-29: 201 Created when `login` is in Cyrillic

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is in Cyrillic, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "терве",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-30"></a>

## SSI-30: 201 Created when `login` is in Chinese characters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is in Chinese characters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "欢迎",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-31"></a>

## SSI-31: 201 Created when `login` is 1 character long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is 1 character long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "t",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-32"></a>

## SSI-32: 201 Created when `login` is 11 characters long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is 11 characters long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "tervetuloaa",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-33"></a>

## SSI-33: 201 Created when `login` is 12 characters long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is 12 characters long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "tervetuuloaa",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-34"></a>

## SSI-34: 201 Created when `login` is a very long string

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is a very long string, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "averylongloginnameyoucannotevenimaginehowlongitisiswear",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-35"></a>

## SSI-35: 201 Created when `login` starts with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` starts with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": " terve",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-36"></a>

## SSI-36: 201 Created when `login` ends with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` ends with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve ",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-37"></a>

## SSI-37: 201 Created when `login` has a space in the middle

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` has a space in the middle, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "ter ve",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-38"></a>

## SSI-38: 201 Created when `login` is a number

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is a number, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": 1234,
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-39"></a>

## SSI-39: 500 Internal Server Error when `login` is sent as `true`

| | |
|---|---|
| **Priority** | Critical |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` is sent as a boolean, the server answers with 500 Internal Server Error and exposes a database error message.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": true,
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 500 Internal Server Error:

```json
{
  "code": 500,
  "message": "operator does not exist: character varying = boolean"
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-40"></a>

## SSI-40: 201 Created when `login` consists of special characters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `login` consists of special characters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "***",
  "password": "1111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-41"></a>

## SSI-41: 201 Created when `password` is 3 digits long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` is 3 digits long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "123",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-42"></a>

## SSI-42: 201 Created when `password` is 5 digits long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` is 5 digits long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "12345",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-43"></a>

## SSI-43: 201 Created when `password` is a very long string

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` is a very long string, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "10000000000000000000000000000000000000000",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-44"></a>

## SSI-44: 201 Created when `password` is sent without quotes

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` is sent without quotes, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": 1111,
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-45"></a>

## SSI-45: 201 Created when `password` starts with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` starts with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": " 111",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-46"></a>

## SSI-46: 201 Created when `password` ends with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` ends with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "111 ",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-47"></a>

## SSI-47: 201 Created when `password` has a space in the middle

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` has a space in the middle, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "11 1",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-48"></a>

## SSI-48: 201 Created when `password` consists of letters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` consists of letters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "lttr",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-49"></a>

## SSI-49: 201 Created when `password` is `true`

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` is `true`, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": true,
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-50"></a>

## SSI-50: 201 Created when `password` consists of special characters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `password` consists of special characters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "****",
  "firstName": "Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-51"></a>

## SSI-51: 201 Created when `firstName` is in Chinese characters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is in Chinese characters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "一只小猫"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-52"></a>

## SSI-52: 201 Created when `firstName` is 1 character long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is 1 character long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "K"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-53"></a>

## SSI-53: 201 Created when `firstName` is 11 characters long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is 11 characters long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "Kissanpentu"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-54"></a>

## SSI-54: 201 Created when `firstName` is 12 characters long

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is 12 characters long, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "Kissanpentuj"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-55"></a>

## SSI-55: 201 Created when `firstName` is a very long string

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is a very long string, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "averylongfirstnameyoucannotevenimaginehowlongitisiswear"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-56"></a>

## SSI-56: 201 Created when `firstName` consists of digits

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` consists of digits, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "1234"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-57"></a>

## SSI-57: 201 Created when `firstName` starts with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` starts with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": " Kissa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-58"></a>

## SSI-58: 201 Created when `firstName` has a space in the middle

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` has a space in the middle, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "Kis sa"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-59"></a>

## SSI-59: 201 Created when `firstName` ends with a space

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` ends with a space, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "Kissa "
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-60"></a>

## SSI-60: 201 Created when `firstName` is `true`

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` is `true`, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": true
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-61"></a>

## SSI-61: 201 Created when `firstName` consists of special characters

| | |
|---|---|
| **Priority** | Medium |
| **Area** | API, `POST /api/v1/autopilot` |
| **Environment** | Test server, API v1 |

**Description.** If `firstName` consists of special characters, the server answers with 201 Created and the autopilot is registered.

**Steps to reproduce**

1. Send `POST /api/v1/autopilot` with the body:

```json
{
  "login": "terve",
  "password": "1111",
  "firstName": "***"
}
```

**Actual result.** Status 201 Created. The autopilot is registered:

```json
{
  "ok": true
}
```

**Expected result.** Status 400 Bad Request with an error message. The autopilot is not registered.

---

<a id="ssi-62"></a>

## SSI-62: Orders of a deleted autopilot are not removed

| | |
|---|---|
| **Priority** | Critical |
| **Area** | API, `DELETE /api/v1/autopilot/:id` |
| **Environment** | Test server, API v1 |

**Description.** After an autopilot is deleted, the order assigned to it is still returned by its tracking number.

**Preconditions**

1. An autopilot with id 1 exists.
2. An order with tracking number 241615 exists and has been accepted by this autopilot.

**Steps to reproduce**

1. Send `DELETE /api/v1/autopilot/1`.
2. Send `GET /api/v1/orders/track?t=241615`.

**Actual result.** Status 200 OK. The order is returned in full (`"inDelivery": true`, `"status": 1`).

**Expected result.** Status 404 Not Found:

```json
{
  "message": "Order not found"
}
```

**Attachments.** Two screenshots (delete response, track response).
