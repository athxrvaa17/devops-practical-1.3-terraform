resource "aws_autoscaling_group" "app" {
  name                = "nimbus-q13-asg"
  min_size            = 2
  desired_capacity    = 2
  max_size            = 6
  vpc_zone_identifier = var.public_subnet_ids

  target_group_arns = [var.target_group_arn]

  health_check_type         = "ELB"
  health_check_grace_period = 300

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "nimbus-q13-asg-instance"
    propagate_at_launch = true
  }
}
