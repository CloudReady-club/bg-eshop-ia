resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = var.bucket_id

  dynamic "rule" {
    for_each = var.lifecycle_rules

    content {
      id     = rule.value.id
      status = rule.value.enabled ? "Enabled" : "Disabled"

      filter {
          prefix = rule.value.prefix
          
      }

      dynamic "transition" {
        for_each = try(rule.value.transition, null) != null ? rule.value.transition : []
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }

      dynamic "expiration" {
        for_each = try(rule.value.expiration_days, null) != null ? [1] : []
        content {
          days = rule.value.expiration_days
        }
      }
      dynamic "noncurrent_version_transition" {
        for_each = try(rule.value.noncurrent_version_transition, null) != null ? [1] : []
        content {
          noncurrent_days          = noncurrent_version_transition.value.days
          storage_class = noncurrent_version_transition.value.storage_class
        }
      }

      dynamic "noncurrent_version_expiration" {
        for_each = try(rule.value.noncurrent_version_expiration_days, null) != null ? [1] : []
        content {
          noncurrent_days = rule.value.noncurrent_version_expiration_days
        }
      }
    }
  }
}