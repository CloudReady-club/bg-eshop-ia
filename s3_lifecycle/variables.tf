variable "bucket_id" {
  description = "S3 bucket ID or name"
  type        = string
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules"
  type = list(object({
    id          = string
    enabled     = bool
    prefix  =string


    transition = optional(list(object({
      days          = number
      storage_class = string
    })))

    expiration_days = optional(number)

    noncurrent_version_transition = optional(list(object({
      days          = number
      storage_class = string
    })))
    noncurrent_version_expiration_days = optional(number)
  }))

  
}