// increase for more quality
$fn = 100;

// enter button details:
button_width = 60;   // button diameter
button_height = 10;  // button height upper part
button_lenght = 30;  // button height total
button_radius = 10;


// don't change:
height1 = 10;
height2 = button_lenght - button_height;
height3 = button_height + 5;
width = button_width + 5;
radius = width / 2;
shaft_width = button_radius + 5;


difference() {
    union() {
        // lower cylinder
        cylinder(h = height1,
                 r1 = radius,
                 r2 = radius - 1, 
                 center = false);

        translate([0, 0, height1]) {
            // inner cylinder
            cylinder(h = height2,
                     r1 = shaft_width + 5, 
                     r2 = shaft_width + 5, 
                     center = false);
        }

        difference() {
            translate([0, 0, height1 + height2]) {
                // top cylinder
                cylinder(h = height3,
                         r1 = radius, 
                         r2 = radius - 1, 
                         center = false);
            }

            translate([0, 0, height1 + height2 + 5]) {
                cylinder(h = height3,
                         r1 = radius - 5, 
                         r2 = radius - 5, 
                         center = false);
            }
        }
    }

    cylinder(h = (height1 + height2 + height3) * 2,
             r1 = shaft_width,
             r2 = shaft_width2,
             center = true);
}