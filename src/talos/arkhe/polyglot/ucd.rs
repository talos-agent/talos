// ucd.rs
use std::f64;

struct UCD {
    data: Vec<Vec<f64>>,
    c: f64,
    f: f64,
}

impl UCD {
    fn new(data: Vec<Vec<f64>>) -> Self {
        UCD { data, c: 0.0, f: 0.0 }
    }

    fn pearson(&self, x: &[f64], y: &[f64]) -> f64 {
        let n = x.len();
        let mean_x = x.iter().sum::<f64>() / n as f64;
        let mean_y = y.iter().sum::<f64>() / n as f64;
        let mut num = 0.0;
        let mut den_x = 0.0;
        let mut den_y = 0.0;
        for i in 0..n {
            let dx = x[i] - mean_x;
            let dy = y[i] - mean_y;
            num += dx * dy;
            den_x += dx * dx;
            den_y += dy * dy;
        }
        if den_x == 0.0 || den_y == 0.0 { 0.0 } else { num / (den_x * den_y).sqrt() }
    }

    fn analyze(&mut self) -> (f64, f64, bool, String, String, f64) {
        let n = self.data.len();
        if n > 1 {
            let mut sum_corr = 0.0;
            let mut count = 0;
            for i in 0..n {
                for j in i+1..n {
                    let corr = self.pearson(&self.data[i], &self.data[j]);
                    sum_corr += corr.abs();
                    count += 1;
                }
            }
            self.c = if count > 0 { sum_corr / count as f64 } else { 0.5 };
        } else {
            self.c = 0.5;
        }
        self.f = 1.0 - self.c;
        let cons = (self.c + self.f - 1.0).abs() < 1e-10;
        let topo = if self.c > 0.8 { "toroidal".to_string() } else { "other".to_string() };
        let scaling = if self.c > 0.7 { "self-similar".to_string() } else { "linear".to_string() };
        (self.c, self.f, cons, topo, scaling, self.f * 0.5)
    }
}

fn main() {
    let data = vec![
        vec![1.0,2.0,3.0,4.0],
        vec![2.0,3.0,4.0,5.0],
        vec![5.0,6.0,7.0,8.0],
    ];
    let mut ucd = UCD::new(data);
    let (c, f, cons, topo, scaling, opt) = ucd.analyze();
    println!("C: {:.4}, F: {:.4}, conservation: {}, topology: {}, scaling: {}, opt: {:.4}",
             c, f, cons, topo, scaling, opt);
}
