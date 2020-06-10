import { PASSWORD_STRENGTH } from "lib/constants"
import { isEmail } from "lib/utilities"

export const passwordStrengthValidator = (rule, value, callback) => {
  let strength = 0
  const { zxcvbn } = window

  if (value && zxcvbn) {
    const result = zxcvbn(value)
    strength = result.score
  }
  if (zxcvbn && strength < PASSWORD_STRENGTH) {
    callback("Password is not strong enough.")
  } else {
    callback()
  }
}

export const emailValidator = (rule, value, callback) => {
  if (typeof value === 'string' && isEmail(value) && value.length < 255) {
    callback();
  } else {
    callback("Email format is invalid.")
  }
  callback()
}
